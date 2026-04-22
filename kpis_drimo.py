import requests
import csv
from datetime import datetime
import os

# 1. CONFIGURACIÓN
GITHUB_TOKEN = ''
REPO_OWNER = '' # Cambiar por tu usuario
REPO_NAME = ''     # Cambiar por tu repositorio

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}
BASE_URL = 'https://api.github.com'
CSV_FILENAME = 'drimo_dataset_prs1.csv'

def obtener_datos_kpis():
    print(f"\nINICIANDO EXTRACCIÓN DE DATOS ({REPO_OWNER}/{REPO_NAME})")
    print("="*60)
    
    # Variables globales para el resumen final en consola
    tiempos_merge_global = []
    tamanos_pr_global = []
    tiempos_rama_global = []
    prs_revisados_global = 0
    prs_con_rechazos_global = 0
    prs_totales_descargados = 0
    prs_validos_procesados = 0

    # 2. EXTRACCIÓN PRs Y GENERACIÓN DE CSV
    url_prs = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    params_prs = {'state': 'closed', 'per_page': 100} 
    res_prs = requests.get(url_prs, headers=HEADERS, params=params_prs)
    
    if res_prs.status_code == 200:
        prs = res_prs.json()
        prs_totales_descargados = len(prs)
        print(f"Conexión exitosa. Se detectaron {prs_totales_descargados} PRs en estado 'cerrado'.")
        print(f"Filtrando PRs válidos y escribiendo datos estructurados en {CSV_FILENAME}...\n")
        
        with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)
            
            escritor_csv.writerow([
                'Repo_Name', 'PR_Number', 'Created_At', 'Merged_At', 'Merge_Time_Hours', 
                'PR_Size_Lines', 'Rejections_Count', 'Branch_Lifetime_Hours'
            ])
            
            for pr in prs:
                if not pr['merged_at']:
                    continue # Ignorar los cancelados (rojos)
                    
                prs_validos_procesados += 1 
                pr_number = pr['number']
                
                creado_str = pr['created_at']
                fusionado_str = pr['merged_at']
                creado_dt = datetime.strptime(creado_str, '%Y-%m-%dT%H:%M:%SZ')
                fusionado_dt = datetime.strptime(fusionado_str, '%Y-%m-%dT%H:%M:%SZ')
            
                # 1. Merge Time
                horas_merge = round((fusionado_dt - creado_dt).total_seconds() / 3600, 2)
                tiempos_merge_global.append(horas_merge)

                # 2. PR Size
                url_pr_detalle = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}"
                res_detalle = requests.get(url_pr_detalle, headers=HEADERS).json()
                lineas_totales = res_detalle.get('additions', 0) + res_detalle.get('deletions', 0)
                tamanos_pr_global.append(lineas_totales)

                # 3. Iteration / Rechazos
                url_reviews = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/reviews"
                res_reviews = requests.get(url_reviews, headers=HEADERS).json()
                rechazos_individuales = 0
                if res_reviews:
                    prs_revisados_global += 1
                    estados = [rev['state'] for rev in res_reviews]
                    rechazos_individuales = estados.count('CHANGES_REQUESTED')
                    if 'CHANGES_REQUESTED' in estados:
                        prs_con_rechazos_global += 1

                # 4. Branch Lifetime
                url_commits = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/commits"
                res_commits = requests.get(url_commits, headers=HEADERS).json()
                horas_rama = 0
                if res_commits:
                    fecha_primer_commit_str = res_commits[0]['commit']['author']['date']
                    primer_commit_dt = datetime.strptime(fecha_primer_commit_str, '%Y-%m-%dT%H:%M:%SZ')
                    horas_rama = round((fusionado_dt - primer_commit_dt).total_seconds() / 3600, 2)
                    tiempos_rama_global.append(horas_rama)

                escritor_csv.writerow([
                    REPO_NAME, pr_number, creado_str, fusionado_str, horas_merge, 
                    lineas_totales, rechazos_individuales, horas_rama
                ])

    else:
        print(f"Error al conectar con GitHub (PRs): Código {res_prs.status_code}")
        return

    # 3. EXTRACCIÓN PARA KPI 3: Build Success Rate
    print("Consultando estado de GitHub Actions (Builds)...")
    url_actions = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    params_actions = {'per_page': 100} 
    res_actions = requests.get(url_actions, headers=HEADERS, params=params_actions)
    
    builds_exitosos = 0
    builds_totales = 0
    
    if res_actions.status_code == 200:
        runs = res_actions.json().get('workflow_runs', [])
        for run in runs:
            if run['status'] == 'completed':
                builds_totales += 1
                if run['conclusion'] == 'success':
                    builds_exitosos += 1


    # 4. PRESENTACIÓN FINAL EN CONSOLA (RESUMEN)
    print("AUDITORÍA DE DATOS:")
    print(f"- Total PRs (Cerrados) detectados:  {prs_totales_descargados}")
    print(f"- Total PRs VÁLIDOS procesados:     {prs_validos_procesados}")
    print(f"- Archivo exportado exitosamente:   {os.getcwd()}\\{CSV_FILENAME}")
    print("-" * 60)
    
    iteracion = (prs_con_rechazos_global / prs_revisados_global * 100) if prs_revisados_global > 0 else 0
    print(f"1. PR Iteration %:         {iteracion:.1f}% ({prs_con_rechazos_global} rechazados de {prs_revisados_global} revisados)")
    
    avg_merge = sum(tiempos_merge_global) / len(tiempos_merge_global) if tiempos_merge_global else 0
    print(f"2. PR Merge Time:          {avg_merge:.2f} horas en promedio")
    
    tasa_builds = (builds_exitosos / builds_totales * 100) if builds_totales > 0 else 0
    print(f"3. Build Success Rate:     {tasa_builds:.1f}% ({builds_exitosos} exitosos de {builds_totales} procesados)")
    
    avg_size = sum(tamanos_pr_global) / len(tamanos_pr_global) if tamanos_pr_global else 0
    print(f"4. PR Size (Promedio):     {avg_size:.0f} líneas modificadas por PR")
    
    avg_rama = sum(tiempos_rama_global) / len(tiempos_rama_global) if tiempos_rama_global else 0
    print(f"5. Branch Lifetime:        {avg_rama:.2f} horas en promedio desde el 1er commit")
    
    print("="*60)

if __name__ == "__main__":
    obtener_datos_kpis()