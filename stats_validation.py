import numpy as np
import scipy.stats as stats
import scikit_posthocs as sp
import json
import os

def cargar_resultados_cv(ruta_json='cv_metrics_results.json'):
    if not os.path.exists(ruta_json):
        return None
    with open(ruta_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def ejecutar_pruebas_estadisticas(resultados_cv):
    """
    Ejecuta un conjunto robusto de pruebas estadísticas comparando
    los accuracies por fold de todos los modelos disponibles.
    Incluye Friedman Test y Nemenyi post-hoc.
    """
    modelos = list(resultados_cv.keys())
    n_modelos = len(modelos)
    n_folds = len(resultados_cv[modelos[0]]['accuracies_folds'])
    
    reporte = {
        'anova_friedman': {},
        'nemenyi': {},
        'n_folds': n_folds
    }
    
    if n_modelos >= 3:
        listas_accuracies = [np.array(resultados_cv[m]['accuracies_folds']) for m in modelos]
        
        # 1. PRUEBA DE FRIEDMAN
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
                # Transponer listas_accuracies para que sean (folds x modelos) o pasar lista de listas
                # scikit-posthocs posthoc_nemenyi asume lista de listas de observaciones
                p_values_matrix = sp.posthoc_nemenyi(listas_accuracies)
                
                # Convertir matriz DataFrame a lista de diccionarios para JSON
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
    
    return reporte

if __name__ == "__main__":
    # Prueba rápida
    resultados = cargar_resultados_cv()
    if resultados:
        rep = ejecutar_pruebas_estadisticas(resultados)
        print(json.dumps(rep, indent=2))
