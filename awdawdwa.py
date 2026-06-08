import pandas as pd
import matplotlib.pyplot as plt
import os

def leer_csv_con_validacion(ruta):
	if not os.path.exists(ruta):
		print(f"Error: El archivo '{ruta}' no existe.")
		return None
	try:
		df = pd.read_csv(ruta)
		if df.empty:
			print("El archivo está vacío.")
			return None
		return df
	except Exception as e:
		print(f"Error al leer el archivo: {e}")
		return None

def graficos_comparativos(df):
	if df is None or df.empty:
		print("No hay datos para graficar.")
		return
	# Validar columnas necesarias
	columnas = ["PR_Size_Lines", "Merge_Time_Hours", "Branch_Lifetime_Hours"]
	for col in columnas:
		if col not in df.columns:
			print(f"Falta la columna '{col}' en el archivo.")
			return
	# Gráfico 1: Tamaño del PR vs Tiempo de Merge
	plt.figure(figsize=(8,5))
	plt.scatter(df["PR_Size_Lines"], df["Merge_Time_Hours"], color='blue')
	plt.xlabel("Tamaño del PR (líneas)")
	plt.ylabel("Tiempo de Merge (horas)")
	plt.title("Tamaño del PR vs Tiempo de Merge")
	plt.grid(True)
	plt.show()

	# Gráfico 2: Tamaño del PR vs Vida de la Rama
	plt.figure(figsize=(8,5))
	plt.scatter(df["PR_Size_Lines"], df["Branch_Lifetime_Hours"], color='green')
	plt.xlabel("Tamaño del PR (líneas)")
	plt.ylabel("Vida de la Rama (horas)")
	plt.title("Tamaño del PR vs Vida de la Rama")
	plt.grid(True)
	plt.show()

	# Gráfico 3: Histograma de Tamaño de PR
	plt.figure(figsize=(8,5))
	plt.hist(df["PR_Size_Lines"], bins=10, color='orange', edgecolor='black')
	plt.xlabel("Tamaño del PR (líneas)")
	plt.ylabel("Cantidad")
	plt.title("Distribución del Tamaño de PR")
	plt.grid(True)
	plt.show()

def estadisticas_descriptivas(df, columna):
	if columna not in df.columns:
		print(f"Columna '{columna}' no encontrada.")
		return {}
	serie = df[columna].dropna()
	return {
		"media": round(serie.mean(), 2),
		"mediana": round(serie.median(), 2),
		"min": round(serie.min(), 2),
		"max": round(serie.max(), 2),
		"std": round(serie.std(), 2),
		"p25": round(serie.quantile(0.25), 2),
		"p75": round(serie.quantile(0.75), 2),
		"count": int(serie.count()),
	}


def imprimir_estadisticas(df, columnas):
	print("\n" + "="*55)
	print("  ESTADÍSTICAS DESCRIPTIVAS")
	print("="*55)
	for col in columnas:
		stats = estadisticas_descriptivas(df, col)
		if not stats:
			continue
		print(f"\n  [{col}]")
		for k, v in stats.items():
			print(f"    {k:<12}: {v}")
	print()


def detectar_outliers_iqr(df, columna):
	if columna not in df.columns:
		return pd.DataFrame()
	serie = df[columna].dropna()
	q1 = serie.quantile(0.25)
	q3 = serie.quantile(0.75)
	iqr = q3 - q1
	limite_inf = q1 - 1.5 * iqr
	limite_sup = q3 + 1.5 * iqr
	outliers = df[(df[columna] < limite_inf) | (df[columna] > limite_sup)]
	return outliers


def reporte_outliers(df, columnas):
	print("\n" + "="*55)
	print("  REPORTE DE OUTLIERS (método IQR)")
	print("="*55)
	for col in columnas:
		outliers = detectar_outliers_iqr(df, col)
		print(f"\n  {col}: {len(outliers)} outliers detectados")
		if not outliers.empty:
			print(outliers[["PR_Number", col]].to_string(index=False))
	print()


def grafico_boxplot(df, columnas, titulo="Distribución de KPIs"):
	disponibles = [c for c in columnas if c in df.columns]
	if not disponibles:
		print("Sin columnas para boxplot.")
		return
	fig, axes = plt.subplots(1, len(disponibles), figsize=(5 * len(disponibles), 5))
	if len(disponibles) == 1:
		axes = [axes]
	for ax, col in zip(axes, disponibles):
		ax.boxplot(df[col].dropna(), patch_artist=True,
				   boxprops=dict(facecolor='lightblue', color='navy'))
		ax.set_title(col)
		ax.set_ylabel("Valor")
		ax.grid(True, linestyle='--', alpha=0.7)
	fig.suptitle(titulo, fontsize=14, fontweight='bold')
	plt.tight_layout()
	plt.show()


def grafico_tendencia_semanal(df, columna_fecha, columna_valor, titulo="Tendencia Semanal"):
	if columna_fecha not in df.columns or columna_valor not in df.columns:
		print(f"Faltan columnas '{columna_fecha}' o '{columna_valor}'.")
		return
	df_copia = df.copy()
	df_copia[columna_fecha] = pd.to_datetime(df_copia[columna_fecha], errors='coerce')
	df_copia = df_copia.dropna(subset=[columna_fecha])
	df_copia["semana"] = df_copia[columna_fecha].dt.to_period("W").apply(lambda r: r.start_time)
	tendencia = df_copia.groupby("semana")[columna_valor].mean().reset_index()
	plt.figure(figsize=(10, 5))
	plt.plot(tendencia["semana"], tendencia[columna_valor], marker='o', color='purple', linewidth=2)
	plt.xlabel("Semana")
	plt.ylabel(f"Promedio {columna_valor}")
	plt.title(titulo)
	plt.xticks(rotation=45)
	plt.grid(True, linestyle='--', alpha=0.6)
	plt.tight_layout()
	plt.show()


def grafico_heatmap_correlacion(df, columnas):
	disponibles = [c for c in columnas if c in df.columns]
	if len(disponibles) < 2:
		print("Se necesitan al menos 2 columnas para la correlación.")
		return
	corr = df[disponibles].corr()
	_, ax = plt.subplots(figsize=(8, 6))
	im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
	plt.colorbar(im, ax=ax)
	ax.set_xticks(range(len(disponibles)))
	ax.set_yticks(range(len(disponibles)))
	ax.set_xticklabels(disponibles, rotation=45, ha='right')
	ax.set_yticklabels(disponibles)
	for i in range(len(disponibles)):
		for j in range(len(disponibles)):
			ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center', fontsize=9)
	ax.set_title("Mapa de Correlación entre KPIs")
	plt.tight_layout()
	plt.show()


def grafico_barras_por_autor(df, columna_autor, columna_valor, top_n=10, titulo="Top Contribuidores"):
	if columna_autor not in df.columns or columna_valor not in df.columns:
		print(f"Columnas necesarias no encontradas.")
		return
	resumen = df.groupby(columna_autor)[columna_valor].sum().nlargest(top_n)
	plt.figure(figsize=(10, 5))
	resumen.plot(kind='bar', color='steelblue', edgecolor='black')
	plt.xlabel("Contribuidor")
	plt.ylabel(columna_valor)
	plt.title(titulo)
	plt.xticks(rotation=45, ha='right')
	plt.grid(True, axis='y', linestyle='--', alpha=0.6)
	plt.tight_layout()
	plt.show()


def grafico_pie_distribucion(df, columna, titulo="Distribución"):
	if columna not in df.columns:
		print(f"Columna '{columna}' no encontrada.")
		return
	counts = df[columna].value_counts()
	plt.figure(figsize=(7, 7))
	plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%',
			startangle=140, colors=plt.cm.Set3.colors)
	plt.title(titulo)
	plt.tight_layout()
	plt.show()


def clasificar_pr_por_tamanio(df):
	if "PR_Size_Lines" not in df.columns:
		return df
	df = df.copy()
	categorias = ["XS", "S", "M", "L"]
	df["PR_Category"] = pd.cut(
		df["PR_Size_Lines"],
		bins=[0, 50, 200, 500, float('inf')],
		labels=categorias
	)
	return df


def clasificar_merge_por_velocidad(df):
	if "Merge_Time_Hours" not in df.columns:
		return df
	df = df.copy()
	df["Merge_Speed"] = pd.cut(
		df["Merge_Time_Hours"],
		bins=[0, 4, 24, 72, float('inf')],
		labels=["Rápido", "Normal", "Lento", "Muy Lento"]
	)
	return df


def tabla_resumen_por_autor(df, columna_autor):
	if columna_autor not in df.columns:
		print(f"Columna '{columna_autor}' no encontrada.")
		return pd.DataFrame()
	columnas_num = df.select_dtypes(include='number').columns.tolist()
	if not columnas_num:
		return pd.DataFrame()
	resumen = df.groupby(columna_autor)[columnas_num].agg(['mean', 'sum', 'count'])
	resumen.columns = ['_'.join(c) for c in resumen.columns]
	return resumen.reset_index()


def guardar_reporte_txt(df, ruta_salida="reporte_kpis.txt"):
	columnas_kpi = ["PR_Size_Lines", "Merge_Time_Hours", "Branch_Lifetime_Hours"]
	with open(ruta_salida, "w", encoding="utf-8") as f:
		f.write("REPORTE DE KPIs DE PRODUCCIÓN\n")
		f.write("="*55 + "\n\n")
		f.write(f"Total de PRs analizados: {len(df)}\n\n")
		for col in columnas_kpi:
			if col not in df.columns:
				continue
			stats = estadisticas_descriptivas(df, col)
			f.write(f"[{col}]\n")
			for k, v in stats.items():
				f.write(f"  {k:<12}: {v}\n")
			f.write("\n")
		outliers_totales = sum(
			len(detectar_outliers_iqr(df, col)) for col in columnas_kpi if col in df.columns
		)
		f.write(f"Total de outliers detectados: {outliers_totales}\n")
	print(f"Reporte guardado en '{ruta_salida}'.")


def filtrar_por_rango_fechas(df, columna_fecha, fecha_inicio, fecha_fin):
	if columna_fecha not in df.columns:
		return df
	df = df.copy()
	df[columna_fecha] = pd.to_datetime(df[columna_fecha], errors='coerce')
	mascara = (df[columna_fecha] >= fecha_inicio) & (df[columna_fecha] <= fecha_fin)
	return df[mascara].reset_index(drop=True)


def filtrar_por_autor(df, columna_autor, autor):
	if columna_autor not in df.columns:
		return df
	return df[df[columna_autor] == autor].reset_index(drop=True)


def calcular_kpi_churn(df):
	if "Additions" not in df.columns or "Deletions" not in df.columns:
		print("Faltan columnas 'Additions' y/o 'Deletions'.")
		return df
	df = df.copy()
	total = df["Additions"] + df["Deletions"]
	df["Churn_Rate_Pct"] = (df["Deletions"] / total.replace(0, float('nan'))) * 100
	df["Churn_Rate_Pct"] = df["Churn_Rate_Pct"].round(2)
	return df


def calcular_kpi_iteration(df):
	if "Reviews_Received" not in df.columns or "Changes_Requested" not in df.columns:
		print("Faltan columnas de revisión.")
		return df
	df = df.copy()
	df["Iteration_Pct"] = (
		df["Changes_Requested"] / df["Reviews_Received"].replace(0, float('nan'))
	) * 100
	df["Iteration_Pct"] = df["Iteration_Pct"].fillna(0).round(2)
	return df


def pipeline_completo(ruta_csv):
	print(f"\nIniciando pipeline para: {ruta_csv}")
	print("="*55)

	df = leer_csv_con_validacion(ruta_csv)
	if df is None:
		return

	columnas_kpi = ["PR_Size_Lines", "Merge_Time_Hours", "Branch_Lifetime_Hours"]
	imprimir_estadisticas(df, columnas_kpi)
	reporte_outliers(df, columnas_kpi)

	df = clasificar_pr_por_tamanio(df)
	df = clasificar_merge_por_velocidad(df)

	if "Additions" in df.columns and "Deletions" in df.columns:
		df = calcular_kpi_churn(df)
	if "Reviews_Received" in df.columns and "Changes_Requested" in df.columns:
		df = calcular_kpi_iteration(df)

	guardar_reporte_txt(df)

	print("\nGenerando gráficos...")
	graficos_comparativos(df)
	grafico_boxplot(df, columnas_kpi, titulo="Boxplot de KPIs")
	grafico_heatmap_correlacion(df, columnas_kpi)

	if "Author" in df.columns:
		grafico_barras_por_autor(df, "Author", "PR_Size_Lines", titulo="Líneas por Autor")

	if "PR_Category" in df.columns:
		grafico_pie_distribucion(df, "PR_Category", titulo="Distribución por Categoría de PR")

	print("\nPipeline completado.")


def grafico_lineas_acumuladas(df, columna_fecha, columna_valor, titulo="Acumulado"):
	if columna_fecha not in df.columns or columna_valor not in df.columns:
		print(f"Faltan columnas necesarias.")
		return
	df_copia = df.copy()
	df_copia[columna_fecha] = pd.to_datetime(df_copia[columna_fecha], errors='coerce')
	df_copia = df_copia.dropna(subset=[columna_fecha]).sort_values(columna_fecha)
	df_copia["acumulado"] = df_copia[columna_valor].cumsum()
	plt.figure(figsize=(10, 5))
	plt.plot(df_copia[columna_fecha], df_copia["acumulado"], color='teal', linewidth=2)
	plt.fill_between(df_copia[columna_fecha], df_copia["acumulado"], alpha=0.2, color='teal')
	plt.xlabel("Fecha")
	plt.ylabel(f"Acumulado {columna_valor}")
	plt.title(titulo)
	plt.xticks(rotation=45)
	plt.grid(True, linestyle='--', alpha=0.6)
	plt.tight_layout()
	plt.show()


def calcular_tasa_aprobacion(df):
	if "Reviews_Received" not in df.columns or "Changes_Requested" not in df.columns:
		return {}
	total_revisados = df["Reviews_Received"].sum()
	total_rechazados = df["Changes_Requested"].sum()
	aprobados = total_revisados - total_rechazados
	tasa = round((aprobados / total_revisados) * 100, 2) if total_revisados > 0 else 0
	return {
		"total_revisados": int(total_revisados),
		"total_rechazados": int(total_rechazados),
		"aprobados_directos": int(aprobados),
		"tasa_aprobacion_pct": tasa,
	}


def imprimir_tasa_aprobacion(df):
	resultado = calcular_tasa_aprobacion(df)
	if not resultado:
		print("Sin datos de revisión.")
		return
	print("\n" + "="*55)
	print("  TASA DE APROBACIÓN DE PRs")
	print("="*55)
	for k, v in resultado.items():
		print(f"  {k:<35}: {v}")
	print()


def comparar_dos_periodos(df, columna_fecha, columna_valor, fecha_corte):
	if columna_fecha not in df.columns or columna_valor not in df.columns:
		return
	df = df.copy()
	df[columna_fecha] = pd.to_datetime(df[columna_fecha], errors='coerce')
	fecha_corte = pd.to_datetime(fecha_corte)
	periodo_a = df[df[columna_fecha] < fecha_corte][columna_valor].dropna()
	periodo_b = df[df[columna_fecha] >= fecha_corte][columna_valor].dropna()
	print(f"\n  Comparación de '{columna_valor}' antes/después de {fecha_corte.date()}")
	print(f"  Periodo A — media: {periodo_a.mean():.2f}, n={len(periodo_a)}")
	print(f"  Periodo B — media: {periodo_b.mean():.2f}, n={len(periodo_b)}")
	if len(periodo_a) > 0 and len(periodo_b) > 0:
		delta = round(periodo_b.mean() - periodo_a.mean(), 2)
		signo = "+" if delta > 0 else ""
		print(f"  Diferencia: {signo}{delta}")
	print()


def grafico_doble_eje(df, columna_x, columna_y1, columna_y2):
	if not all(c in df.columns for c in [columna_x, columna_y1, columna_y2]):
		print("Faltan columnas para gráfico de doble eje.")
		return
	fig, ax1 = plt.subplots(figsize=(10, 5))
	ax1.set_xlabel(columna_x)
	ax1.set_ylabel(columna_y1, color='blue')
	ax1.plot(df[columna_x], df[columna_y1], color='blue', marker='o', label=columna_y1)
	ax1.tick_params(axis='y', labelcolor='blue')
	ax2 = ax1.twinx()
	ax2.set_ylabel(columna_y2, color='red')
	ax2.plot(df[columna_x], df[columna_y2], color='red', marker='s', linestyle='--', label=columna_y2)
	ax2.tick_params(axis='y', labelcolor='red')
	fig.suptitle(f"{columna_y1} vs {columna_y2}", fontsize=13, fontweight='bold')
	fig.tight_layout()
	plt.show()


def contar_prs_por_estado_categoria(df):
	if "PR_Category" not in df.columns:
		df = clasificar_pr_por_tamanio(df)
	if "PR_Category" not in df.columns:
		print("No se pudo calcular PR_Category.")
		return pd.DataFrame()
	return df["PR_Category"].value_counts().reset_index().rename(
		columns={"index": "Categoría", "PR_Category": "Cantidad"}
	)


def imprimir_tabla_categorias(df):
	tabla = contar_prs_por_estado_categoria(df)
	if tabla.empty:
		return
	print("\n" + "="*40)
	print("  DISTRIBUCIÓN POR CATEGORÍA DE PR")
	print("="*40)
	print(tabla.to_string(index=False))
	print()


if __name__ == "__main__":
	ruta = "drimo_dataset_prs.csv"
	df = leer_csv_con_validacion(ruta)
	graficos_comparativos(df)
	pipeline_completo(ruta)