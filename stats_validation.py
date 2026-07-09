import numpy as np
import scipy.stats as stats
import json
import os

def cargar_resultados_cv(ruta_json='cv_metrics_results.json'):
    """Carga los resultados de la validación cruzada desde el archivo JSON"""
    if not os.path.exists(ruta_json):
        return None
    with open(ruta_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def ejecutar_pruebas_estadisticas(resultados_cv):
    """
    Ejecuta un conjunto robusto de pruebas estadísticas comparando
    los accuracies por fold de todos los modelos disponibles.
    
    Retorna un diccionario estructurado con los resultados e interpretaciones.
    """
    modelos = list(resultados_cv.keys())
    n_modelos = len(modelos)
    n_folds = len(resultados_cv[modelos[0]]['accuracies_folds'])
    
    reporte = {
        'anova_friedman': {},
        'comparaciones_pares': [],
        'n_folds': n_folds
    }
    
    # 1. PRUEBA DE FRIEDMAN (Comparación global no paramétrica)
    if n_modelos >= 3:
        # Reunir las listas de accuracies de cada modelo
        listas_accuracies = [resultados_cv[m]['accuracies_folds'] for m in modelos]
        
        try:
            stat, p_val = stats.friedmanchisquare(*listas_accuracies)
            interpretacion = (
                "Existe una diferencia estadísticamente significativa en el rendimiento "
                "general entre al menos dos de los modelos (p < 0.05)."
                if p_val < 0.05 else
                "No hay evidencia estadística de diferencias significativas en el rendimiento "
                "general entre los modelos evaluados (p >= 0.05)."
            )
            reporte['anova_friedman'] = {
                'estadistico': float(stat),
                'p_valor': float(p_val),
                'significativo': bool(p_val < 0.05),
                'interpretacion': interpretacion
            }
        except Exception as e:
            reporte['anova_friedman'] = {
                'error': f"Error en test de Friedman: {str(e)}"
            }
    else:
        reporte['anova_friedman'] = {
            'info': "Se requieren al menos 3 modelos para realizar la prueba de Friedman."
        }
        
    # 2. COMPARACIÓN POR PARES (t-Student emparejado y Wilcoxon)
    # Compara cada combinación de dos modelos
    import itertools
    for mod1, mod2 in itertools.combinations(modelos, 2):
        acc1 = np.array(resultados_cv[mod1]['accuracies_folds'])
        acc2 = np.array(resultados_cv[mod2]['accuracies_folds'])
        
        # A. Prueba t-Student emparejada
        try:
            t_stat, t_pval = stats.ttest_rel(acc1, acc2)
            t_significativo = bool(t_pval < 0.05)
        except Exception as e:
            t_stat, t_pval, t_significativo = 0.0, 1.0, False
            
        # B. Prueba de rangos con signo de Wilcoxon (no paramétrica)
        try:
            w_stat, w_pval = stats.wilcoxon(acc1, acc2)
            w_significativo = bool(w_pval < 0.05)
        except Exception as e:
            # Puede fallar si las diferencias son todas cero
            w_stat, w_pval, w_significativo = 0.0, 1.0, False
            
        # Interpretación consolidada por pares
        if t_significativo or w_significativo:
            media_diff = np.mean(acc1) - np.mean(acc2)
            mejor_modelo = mod1 if media_diff > 0 else mod2
            peor_modelo = mod2 if media_diff > 0 else mod1
            interpretacion = (
                f"El modelo {mejor_modelo.upper()} supera significativamente "
                f"a {peor_modelo.upper()} en exactitud por fold (p < 0.05)."
            )
        else:
            interpretacion = (
                f"No hay diferencia estadísticamente significativa en la exactitud "
                f"entre {mod1.upper()} y {mod2.upper()} (p >= 0.05)."
            )
            
        reporte['comparaciones_pares'].append({
            'modelo1': mod1,
            'modelo2': mod2,
            't_student': {
                'estadistico': float(t_stat) if not np.isnan(t_stat) else 0.0,
                'p_valor': float(t_pval) if not np.isnan(t_pval) else 1.0,
                'significativo': t_significativo
            },
            'wilcoxon': {
                'estadistico': float(w_stat),
                'p_valor': float(w_pval),
                'significativo': w_significativo
            },
            'interpretacion': interpretacion
        })
        
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
