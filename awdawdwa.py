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

if __name__ == "__main__":
	ruta = "drimo_dataset_prs.csv"
	df = leer_csv_con_validacion(ruta)
	graficos_comparativos(df)