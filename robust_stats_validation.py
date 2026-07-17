import numpy as np
import scipy.stats as stats
import os
import json
import warnings
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Configurar encoding UTF-8 para evitar errores de consola en Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Desactivar advertencias para limpieza de consola
warnings.filterwarnings('ignore')

class RobustStatisticalValidation:
    """
    Biblioteca de Validación Estadística Robusta para Redes Neuronales.
    Diseñada para evaluar estabilidad, especificación, comparación de arquitecturas 
    y generalización en modelos agrícolas y clínicos.
    """
    
    @staticmethod
    def test_kolmogorov_smirnov_logit_gaps(gaps_seed1, gaps_seed2):
        """
        1. Evalúa la Estabilidad comparando distribuciones de logit gaps entre 
           dos ejecuciones con distintas semillas.
           H0: Ambas distribuciones provienen del mismo comportamiento del modelo.
        """
        ks_stat, p_val = stats.ks_2samp(gaps_seed1, gaps_seed2)
        
        significativo = p_val < 0.05
        interpretacion = (
            "⚠️ DIFERENCIA DETECTADA: Las distribuciones de confianza del modelo cambian significativamente con la semilla aleatoria."
            if significativo else
            "✅ ESTABLE: Las distribuciones de confianza son equivalentes bajo diferentes semillas."
        )
        
        return {
            'prueba': 'Kolmogorov-Smirnov (Logit Gaps)',
            'estadistico_ks': float(ks_stat),
            'p_valor': float(p_val),
            'significativo': bool(significativo),
            'interpretacion': interpretacion
        }
        
    @staticmethod
    def calcular_alpha_trimming(accuracies, alpha=0.1):
        """
        2. Prueba de alpha-trimming para medir la representatividad de la semilla.
           Elimina los percentiles extremos (outliers de entrenamiento) para encontrar
           una estimación robusta de la capacidad del modelo.
        """
        accuracies_sorted = np.sort(accuracies)
        n = len(accuracies)
        k = int(n * alpha)
        
        if k > 0:
            trimmed_data = accuracies_sorted[k:-k]
        else:
            trimmed_data = accuracies_sorted
            
        media_trimmed = np.mean(trimmed_data)
        std_trimmed = np.std(trimmed_data)
        
        # Identificar las semillas más representativas (las más cercanas a la media trimmed)
        distancia_a_media = np.abs(accuracies - media_trimmed)
        indice_representativo = int(np.argmin(distancia_a_media))
        
        return {
            'prueba': 'Nivel de alpha-trimming',
            'alpha_aplicado': float(alpha),
            'total_muestras': n,
            'muestras_recortadas': 2 * k,
            'media_trimmed': float(media_trimmed),
            'desviacion_trimmed': float(std_trimmed),
            'indice_semilla_representativa': indice_representativo,
            'valor_representativo': float(accuracies[indice_representativo])
        }

    @staticmethod
    def test_mann_whitney_u(scores_modelo_a, scores_modelo_b):
        """
        3. Compara de forma no paramétrica el rendimiento de dos arquitecturas.
           H0: No hay diferencia sistemática de rendimiento entre ambos modelos.
        """
        stat, p_val = stats.mannwhitneyu(scores_modelo_a, scores_modelo_b, alternative='two-sided')
        
        significativo = p_val < 0.05
        interpretacion = (
            "✅ DIFERENCIA SIGNIFICATIVA: Una arquitectura rinde sistemáticamente mejor que la otra."
            if significativo else
            "❌ SIN DIFERENCIA SIGNIFICATIVA: El rendimiento de ambas arquitecturas es equivalente."
        )
        
        return {
            'prueba': 'Prueba de Mann-Whitney U',
            'estadistico_u': float(stat),
            'p_valor': float(p_val),
            'significativo': bool(significativo),
            'interpretacion': interpretacion
        }

    @staticmethod
    def test_pitman_morgan_varianzas(errores_modelo_a, errores_modelo_b):
        """
        4. Prueba de Pitman-Morgan para igualdad de varianzas de error en muestras correlacionadas.
           Útil para seleccionar el modelo más simple si la varianza del error no difiere.
           H0: Las varianzas de los errores son iguales.
        """
        n = len(errores_modelo_a)
        if n != len(errores_modelo_b):
            raise ValueError("Los vectores de errores deben tener el mismo tamaño.")
            
        e_a = np.array(errores_modelo_a)
        e_b = np.array(errores_modelo_b)
        
        # Sumas y Diferencias
        S = e_a + e_b
        D = e_a - e_b
        
        # Coeficiente de correlación de Pearson entre S y D
        r, _ = stats.pearsonr(S, D)
        
        if np.abs(r) >= 1.0:
            t_stat = np.inf
            p_val = 0.0
        else:
            # Estadístico t
            t_stat = r * np.sqrt((n - 2) / (1 - r**2))
            # p-valor de dos colas
            p_val = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=n-2))
            
        significativo = p_val < 0.05
        interpretacion = (
            "✅ DIFERENCIA EN ESTABILIDAD: Las varianzas de error difieren. Elige el modelo con menor dispersión."
            if significativo else
            "❌ EQUIVALENCIA DE ESTABILIDAD: Varianzas iguales. Selecciona el modelo más simple (parsimonia)."
        )
        
        return {
            'prueba': 'Pitman-Morgan (Igualdad de Varianzas de Error)',
            'correlacion_r': float(r),
            'estadistico_t': float(t_stat) if not np.isinf(t_stat) else "inf",
            'p_valor': float(p_val),
            'significativo': bool(significativo),
            'interpretacion': interpretacion
        }

    @staticmethod
    def test_lagrange_multiplier_heteroscedasticity(residuos, predicciones):
        """
        5. Prueba de Multiplicadores de Lagrange (LM) tipo Breusch-Pagan robusta.
           Diagnostica si el modelo falla al capturar patrones sistemáticos en la varianza
           (p. ej., variaciones extremas de luz en hojas de maíz).
           H0: Homocedasticidad (varianza constante del error).
        """
        residuos = np.array(residuos)
        predicciones = np.array(predicciones)
        
        # Residuos al cuadrado
        u2 = residuos**2
        u2_mean = np.mean(u2)
        
        # Variable independiente: predicciones del modelo linealizada
        X = np.column_stack((np.ones_like(predicciones), predicciones))
        
        # Regresión de u^2 sobre predicciones
        beta = np.linalg.lstsq(X, u2, rcond=None)[0]
        u2_fit = X.dot(beta)
        
        # R-cuadrado de la regresión auxiliar
        ss_tot = np.sum((u2 - u2_mean)**2)
        if ss_tot == 0:
            r2 = 0.0
        else:
            ss_res = np.sum((u2 - u2_fit)**2)
            r2 = 1.0 - (ss_res / ss_tot)
            
        # Estadístico LM = n * R2
        n = len(residuos)
        lm_stat = n * r2
        
        # Grados de libertad = número de variables independientes en la regresión auxiliar (1)
        p_val = 1.0 - stats.chi2.cdf(lm_stat, df=1)
        
        significativo = p_val < 0.05
        interpretacion = (
            "⚠️ ERROR DE ESPECIFICACIÓN: Hay heterocedasticidad significativa. El modelo pierde patrones en condiciones críticas."
            if significativo else
            "✅ ESPECIFICACIÓN CORRECTA: Varianza del error constante (homocedasticidad)."
        )
        
        return {
            'prueba': 'Breusch-Pagan Lagrange Multiplier (LM) robusto',
            'r_cuadrado_auxiliar': float(r2),
            'estadistico_lm': float(lm_stat),
            'p_valor': float(p_val),
            'significativo': bool(significativo),
            'interpretacion': interpretacion
        }

    @staticmethod
    def test_e_c2st_robustness(activaciones_limpias, activaciones_ruido, alpha=0.05):
        """
        6. Classifier Two-Sample Test secuencial (E-C2ST) mediante E-values.
           Evalúa si el modelo se comporta de la misma forma ante perturbaciones (ruido, luz).
           H0: Las distribuciones de activaciones internas son idénticas (modelo robusto).
        """
        act_c = np.array(activaciones_limpias)
        act_r = np.array(activaciones_ruido)
        
        # Crear etiquetas: 0 = limpio, 1 = perturbado
        X = np.vstack((act_c, act_r))
        y = np.concatenate((np.zeros(len(act_c)), np.ones(len(act_r))))
        
        # Dividir secuencialmente para entrenar el clasificador detector y calcular E-values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42, stratify=y)
        
        clf = RandomForestClassifier(n_estimators=30, random_state=42)
        clf.fit(X_train, y_train)
        
        # Predicciones de probabilidad sobre el conjunto de test
        probs = clf.predict_proba(X_test)
        
        # Calcular E-values secuenciales
        e_values = []
        for i, y_true in enumerate(y_test):
            p_y = probs[i, int(y_true)]
            # E-value individual (relación de verosimilitud bajo H1 vs H0=0.5)
            e_val = p_y / 0.5
            e_values.append(e_val)
            
        # E-value acumulado (producto secuencial)
        e_acumulado = np.prod(e_values)
        
        # Criterio de parada / rechazo: E_N > 1 / alpha
        umbral = 1.0 / alpha
        significativo = e_acumulado > umbral
        
        interpretacion = (
            f"⚠️ PERTURBACIÓN DETECTADA (E={e_acumulado:.2f} > {umbral}): El modelo altera significativamente su comportamiento ante ruido."
            if significativo else
            f"✅ ROBUSTO (E={e_acumulado:.2f} <= {umbral}): El modelo conserva su distribución interna de características."
        )
        
        return {
            'prueba': 'Sequential Classifier Two-Sample Test (E-C2ST)',
            'e_value_acumulado': float(e_acumulado) if not np.isinf(e_acumulado) else "inf",
            'umbral_rechazo': float(umbral),
            'significativo': bool(significativo),
            'interpretacion': interpretacion
        }

if __name__ == "__main__":
    print("=" * 80)
    print("[INFO] SIMULACION DE PRUEBAS ESTADISTICAS ROBUSTAS PARA DETECTOR DE ENFERMEDADES")
    print("=" * 80)
    
    np.random.seed(42)
    validator = RobustStatisticalValidation()
    
    # 1. Simulación Kolmogorov-Smirnov
    gaps_run1 = np.random.normal(loc=2.5, scale=0.5, size=100)
    gaps_run2 = np.random.normal(loc=2.45, scale=0.55, size=100)
    ks_results = validator.test_kolmogorov_smirnov_logit_gaps(gaps_run1, gaps_run2)
    print(f"\n[1/6] {ks_results['prueba']}:")
    print(f"      - p-valor: {ks_results['p_valor']:.6f}")
    print(f"      - Resultado: {ks_results['interpretacion']}")
    
    # 2. Simulación Alpha-Trimming
    seed_accuracies = np.array([0.88, 0.89, 0.72, 0.90, 0.88, 0.91, 0.65, 0.89, 0.90, 0.87])
    trim_results = validator.calcular_alpha_trimming(seed_accuracies, alpha=0.1)
    print(f"\n[2/6] {trim_results['prueba']}:")
    print(f"      - Media Recortada (alpha=10%): {trim_results['media_trimmed']:.4f}")
    print(f"      - Semilla mas estable recomendada: Indice {trim_results['indice_semilla_representativa']} (Valor: {trim_results['valor_representativo']:.4f})")
    
    # 3. Simulación Mann-Whitney U
    scores_resnet = np.random.normal(loc=0.91, scale=0.02, size=15)
    scores_efficientnet = np.random.normal(loc=0.88, scale=0.03, size=15)
    mw_results = validator.test_mann_whitney_u(scores_resnet, scores_efficientnet)
    print(f"\n[3/6] {mw_results['prueba']}:")
    print(f"      - p-valor: {mw_results['p_valor']:.6f}")
    print(f"      - Resultado: {mw_results['interpretacion']}")
    
    # 4. Simulación Pitman-Morgan
    errores_resnet = np.random.normal(loc=0.0, scale=0.1, size=100)
    errores_mobilenet = np.random.normal(loc=0.0, scale=0.12, size=100)
    pm_results = validator.test_pitman_morgan_varianzas(errores_resnet, errores_mobilenet)
    print(f"\n[4/6] {pm_results['prueba']}:")
    print(f"      - p-valor: {pm_results['p_valor']:.6f}")
    print(f"      - Resultado: {pm_results['interpretacion']}")
    
    # 5. Simulación Lagrange Multiplier (LM)
    predicciones = np.random.uniform(low=0.1, high=0.9, size=200)
    residuos_BP = np.random.normal(loc=0.0, scale=predicciones * 0.3, size=200) # Heterocedástico
    lm_results = validator.test_lagrange_multiplier_heteroscedasticity(residuos_BP, predicciones)
    print(f"\n[5/6] {lm_results['prueba']}:")
    print(f"      - p-valor: {lm_results['p_valor']:.6f}")
    print(f"      - Resultado: {lm_results['interpretacion']}")
    
    # 6. Simulación E-C2ST
    activaciones_limpias = np.random.normal(loc=0.0, scale=1.0, size=(100, 10))
    activaciones_ruido = np.random.normal(loc=0.4, scale=1.1, size=(100, 10)) # Con perturbación
    ec2st_results = validator.test_e_c2st_robustness(activaciones_limpias, activaciones_ruido, alpha=0.05)
    print(f"\n[6/6] {ec2st_results['prueba']}:")
    print(f"      - E-value Acumulado: {ec2st_results['e_value_acumulado']}")
    print(f"      - Umbral de Rechazo (1/alpha): {ec2st_results['umbral_rechazo']:.1f}")
    print(f"      - Resultado: {ec2st_results['interpretacion']}")
    print("\n" + "=" * 80)
