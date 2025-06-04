import pandas as pd

# Cargar el archivo original
archivo_entrada = "data/nayarit2.xlsx"
df = pd.read_excel(archivo_entrada)

# Reemplazar todos los asteriscos (*) por 0
df = df.replace("*", 0)

# Guardar archivo limpio
archivo_salida = "data/nayarit2_limpio.xlsx"
df.to_excel(archivo_salida, index=False)

print(f"Archivo limpio guardado como: {archivo_salida}")
