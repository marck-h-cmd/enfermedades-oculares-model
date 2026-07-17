import numpy as np
import scipy.stats as stats
import scikit_posthocs as sp
import json
import os
import sys

# Configurar encoding UTF-8 para evitar errores de consola en Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def cargar_resultados_cv(ruta_json='cv_metrics_results.json'):
    """Carga los resultados de la validación cruzada desde el archivo JSON"""
    if not os.path.exists(ruta_json):
        return None
    with open(ruta_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def corregir_p_valores_holm(p_valores):
    """
    Aplica la corrección secuencial de Holm-Bonferroni a una lista de p-valores.
    Garantiza que la tasa de error por familia (FWER) se mantenga controlada.
    """
    m = len(p_valores)
    if m == 0:
        return []
    
    indices_y_p = sorted(enumerate(p_valores), key=lambda x: x[1])
    p_corregidos = [0.0] * m
    max_prev = 0.0
    
    for rango, (idx_original, p_val) in enumerate(indices_y_p):
        multiplicador = m - rango
        p_adj = min(1.0, p_val * multiplicador)
        max_prev = max(max_prev, p_adj)
        p_corregidos[idx_original] = max_prev
        
    return p_corregidos

def ejecutar_pruebas_estadisticas(resultados_cv):
    """
    Ejecuta un conjunto robusto de pruebas estadísticas comparando
    los accuracies por fold de todos los modelos disponibles.
    Incluye Friedman Test, Nemenyi post-hoc y comparaciones por pares con Shapiro-Wilk,
    t-Student, Wilcoxon, d de Cohen y Holm-Bonferroni.
    """
    modelos = list(resultados_cv.keys())
    n_modelos = len(modelos)
    n_folds = len(resultados_cv[modelos[0]]['accuracies_folds'])
    
    reporte = {
        'anova_friedman': {},
        'nemenyi': {},
        'comparaciones_pares': [],
        'n_folds': n_folds
    }
    
    # 1. PRUEBA DE FRIEDMAN (Comparación global no paramétrica)
    if n_modelos >= 3:
        listas_accuracies = [np.array(resultados_cv[m]['accuracies_folds']) for m in modelos]
        
        try:
            stat, p_val = stats.friedmanchisquare(*listas_accuracies)
            
            # Sanitizar posibles NaNs a flotantes
            if np.isnan(stat): stat = 0.0
            if np.isnan(p_val): p_val = 1.0
                
            interpretacion = (
                "Existe una diferencia estadísticamente significativa en el rendimiento general (p < 0.05)."
                if p_val < 0.05 else
                "No hay evidencia estadística de diferencias significativas en el rendimiento general (p >= 0.05)."
            )
            reporte['anova_friedman'] = {
                'estadistico': float(stat),
                'p_valor': float(p_val),
                'significativo': bool(p_val < 0.05),
                'interpretacion': interpretacion
            }
            
            # 2. PRUEBA DE NEMENYI (Si Friedman es significativo)
            if p_val < 0.05:
                p_values_matrix = sp.posthoc_nemenyi(listas_accuracies)
                
                # Convertir matriz DataFrame a diccionario para JSON
                matrix_dict = {}
                for i, m1 in enumerate(modelos):
                    matrix_dict[m1] = {}
                    for j, m2 in enumerate(modelos):
                        pval = float(p_values_matrix.iloc[i, j])
                        matrix_dict[m1][m2] = pval if not np.isnan(pval) else 1.0
                
                reporte['nemenyi'] = {
                    'realizado': True,
                    'matriz_p_valores': matrix_dict,
                    'modelos': modelos
                }
            else:
                reporte['nemenyi'] = {
                    'realizado': False,
                    'razon': 'La prueba de Friedman no fue significativa, no procede prueba post-hoc.'
                }
                
        except Exception as e:
            reporte['anova_friedman'] = {
                'error': f"Error en test de Friedman: {str(e)}"
            }
    else:
        reporte['anova_friedman'] = {
            'info': "Se requieren al menos 3 modelos para realizar la prueba de Friedman."
        }
        
    # 3. COMPARACIÓN POR PARES (t-Student emparejado y Wilcoxon)
    import itertools
    pares = list(itertools.combinations(modelos, 2))
    
    t_pvals_raw = []
    w_pvals_raw = []
    lista_comparaciones = []
    
    for mod1, mod2 in pares:
        acc1 = np.array(resultados_cv[mod1]['accuracies_folds'])
        acc2 = np.array(resultados_cv[mod2]['accuracies_folds'])
        
        diff = acc1 - acc2
        
        # A. Prueba de normalidad de Shapiro-Wilk sobre la diferencia
        try:
            shap_stat, shap_pval = stats.shapiro(diff)
            es_normal = bool(shap_pval >= 0.05)
        except Exception:
            shap_stat, shap_pval, es_normal = 0.0, 0.0, False
            
        # B. Cálculo de tamaño del efecto (Cohen's d para muestras pareadas)
        mean_diff = np.mean(diff)
        std_diff = np.std(diff, ddof=1)
        cohens_d = mean_diff / std_diff if std_diff > 0 else 0.0
        
        # Clasificación del tamaño del efecto según la regla de Cohen (1988)
        abs_d = abs(cohens_d)
        if abs_d >= 0.8:
            interpretacion_d = "Grande"
        elif abs_d >= 0.5:
            interpretacion_d = "Mediana"
        elif abs_d >= 0.2:
            interpretacion_d = "Pequeña"
        else:
            interpretacion_d = "Despreciable"
            
        # C. Prueba t-Student emparejada
        try:
            t_stat, t_pval = stats.ttest_rel(acc1, acc2)
            if np.isnan(t_pval):
                t_pval = 1.0
        except Exception:
            t_stat, t_pval = 0.0, 1.0
            
        # D. Prueba de rangos con signo de Wilcoxon
        try:
            w_stat, w_pval = stats.wilcoxon(acc1, acc2)
        except Exception:
            w_stat, w_pval = 0.0, 1.0
            
        t_pvals_raw.append(t_pval)
        w_pvals_raw.append(w_pval)
        
        lista_comparaciones.append({
            'modelo1': mod1,
            'modelo2': mod2,
            'shapiro': {
                'estadistico': float(shap_stat),
                'p_valor': float(shap_pval),
                'normal': es_normal
            },
            'cohens_d': {
                'valor': float(cohens_d),
                'interpretacion': interpretacion_d
            },
            't_student': {
                'estadistico': float(t_stat) if not np.isnan(t_stat) else 0.0,
                'p_valor_original': float(t_pval)
            },
            'wilcoxon': {
                'estadistico': float(w_stat),
                'p_valor_original': float(w_pval)
            }
        })
        
    # Aplicar corrección de Holm-Bonferroni
    t_pvals_adj = corregir_p_valores_holm(t_pvals_raw)
    w_pvals_adj = corregir_p_valores_holm(w_pvals_raw)
    
    for idx, comp in enumerate(lista_comparaciones):
        mod1 = comp['modelo1']
        mod2 = comp['modelo2']
        acc1 = np.array(resultados_cv[mod1]['accuracies_folds'])
        acc2 = np.array(resultados_cv[mod2]['accuracies_folds'])
        
        p_t_adj = t_pvals_adj[idx]
        p_w_adj = w_pvals_adj[idx]
        
        comp['t_student']['p_valor_corregido'] = p_t_adj
        comp['t_student']['significativo'] = bool(p_t_adj < 0.05)
        
        comp['wilcoxon']['p_valor_corregido'] = p_w_adj
        comp['wilcoxon']['significativo'] = bool(p_w_adj < 0.05)
        
        # Determinar qué prueba reportar según test de normalidad (Shapiro-Wilk)
        normal = comp['shapiro']['normal']
        p_seleccionado = p_t_adj if normal else p_w_adj
        significativo_final = p_seleccionado < 0.05
        
        if significativo_final:
            media_diff = np.mean(acc1) - np.mean(acc2)
            peor_modelo = mod1 if media_diff < 0 else mod2
            mejor_modelo = mod2 if media_diff < 0 else mod1
            metodo_usado = "t-Student corregido" if normal else "Wilcoxon corregido"
            interpretacion = (
                f"El modelo {mejor_modelo.upper()} supera significativamente "
                f"a {peor_modelo.upper()} en exactitud ({metodo_usado} p={p_seleccionado:.4f}, "
                f"d de Cohen={comp['cohens_d']['valor']:.2f} [{comp['cohens_d']['interpretacion']}])."
            )
        else:
            interpretacion = (
                f"No hay diferencia estadísticamente significativa en la exactitud "
                f"entre {mod1.upper()} y {mod2.upper()} (p-valor corregido p={p_seleccionado:.4f})."
            )
            
        comp['interpretacion'] = interpretacion
        reporte['comparaciones_pares'].append(comp)
        
    return reporte

if __name__ == "__main__":
    # Prueba rápida
    resultados = cargar_resultados_cv()
    if resultados:
        rep = ejecutar_pruebas_estadisticas(resultados)
        print("Prueba Friedman:", rep['anova_friedman'])
        print("Comparaciones pares:", len(rep['comparaciones_pares']))
    else:
        print("No se encontraron resultados de validación cruzada para analizar.")
