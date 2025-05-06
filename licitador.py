import pandas as pd
import unicodedata
import os
import re

from descargar_y_extraer import descargar_y_extraer_xlsx
from tqdm import tqdm
from datetime import datetime
from datetime import datetime, timedelta


# ──────────────── FUNCIONES ──────────────── #

def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8").lower()

def detectar_palabras(texto):
    texto = normalizar(texto)
    return [normalizar(k) for k in keywords if re.search(rf"\b{re.escape(normalizar(k))}\b", texto)]


def contiene_excluidas(texto):
    texto = normalizar(texto)
    return any(re.search(rf"\b{re.escape(normalizar(e))}\b", texto) for e in excluidas)

def leer_config(path="config.txt"):
    config = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                clave, valor = line.strip().split("=", 1)
                config[clave.strip()] = valor.strip()
    return config


# ──────────────── CONFIGURACIÓN ──────────────── #

url_zip = "https://www.mercadopublico.cl/Portal/att.ashx?id=5"
archivo_licitaciones = descargar_y_extraer_xlsx(url_zip)

archivo_palabras_clave = "palabras_clave.txt"
archivo_exclusiones = "palabras_excluidas.txt"

# Leer configuración
config = leer_config()
dias = int(config.get("dias", 15))  # default = 15 días si no está definido

# ──────────────── LECTURA DE ARCHIVOS ──────────────── #

with open(archivo_palabras_clave, "r", encoding="utf-8") as f:
    keywords = [normalizar(line.strip()) for line in f if line.strip()]

with open(archivo_exclusiones, "r", encoding="utf-8") as f:
    excluidas = [normalizar(line.strip()) for line in f if line.strip()]

df_inicial = pd.read_excel(archivo_licitaciones)
for idx, row in df_inicial.iterrows():
    if row.notna().sum() > 5:
        header_row_index = idx
        break

df = pd.read_excel(archivo_licitaciones, header=header_row_index)

# ──────────────── FILTRO FECHA ──────────────── #

df["Unnamed: 9"] = pd.to_datetime(df["Unnamed: 9"], format="%d-%m-%Y %H:%M:%S", errors='coerce')
hoy = datetime.now()
fecha_limite = hoy - timedelta(days=dias)
df = df[df["Unnamed: 9"] >= fecha_limite]

# ──────────────── TEXTO NORMALIZADO ──────────────── #

columnas_texto = [
    "Unnamed: 4",   # Nombre Adquisición
    "Unnamed: 5",   # Descripción
    "Unnamed: 11",  # Descripción del producto/servicio
    "Unnamed: 15"   # Genérico
]

df["texto_completo"] = df[columnas_texto].astype(str).apply(lambda fila: normalizar(" ".join(fila)), axis=1)

# ──────────────── DETECCIÓN DE PALABRAS CLAVE ──────────────── #

tqdm.pandas(desc="🔍 Buscando coincidencias")
df["palabras_clave_detectadas"] = df["texto_completo"].progress_apply(detectar_palabras)
df["match"] = df["palabras_clave_detectadas"].apply(lambda x: len(x) > 0)
df_filtradas = df[df["match"] == True].copy()

# ──────────────── DETECCIÓN DE EXCLUSIONES ──────────────── #

df_filtradas["tiene_excluidas"] = df_filtradas["texto_completo"].apply(contiene_excluidas)
df_resultado = df_filtradas[df_filtradas["tiene_excluidas"] == False].copy()

# ──────────────── LIMPIEZA Y FORMATO FINAL ──────────────── #

columnas_a_eliminar = [col for col in df_resultado.columns if (
    "unnamed" in str(col).lower() and df_resultado[col].isna().all()
)]
df_resultado.drop(columns=columnas_a_eliminar, inplace=True)

renombres = {
    "Unnamed: 1": "Número Adquisición",
    "Unnamed: 2": "Tipo Adquisición",
    "Unnamed: 4": "Nombre Adquisición",
    "Unnamed: 5": "Descripción",
    "Unnamed: 6": "Organismo",
    "Unnamed: 7": "Región",
    "Unnamed: 9": "Fecha Publicación",
    "Unnamed: 10": "Fecha Cierre",
    "Unnamed: 11": "Descripción Producto",
    "Unnamed: 12": "Código ONU",
    "Unnamed: 13": "Unidad de Medida",
    "Unnamed: 14": "Cantidad",
    "Unnamed: 15": "Genérico",
    "Unnamed: 16": "Nivel 1",
    "Unnamed: 17": "Nivel 2",
    "Unnamed: 18": "Nivel 3",
}
df_resultado.rename(columns=renombres, inplace=True)

columnas_excedentes = {"match", "tiene_excluidas"}
df_resultado.drop(columns=columnas_excedentes, inplace=True)


# ──────────────── GUARDAR RESULTADO ──────────────── #

fecha_hoy = datetime.now().strftime("%Y%m%d")
nombre_base = f"licitaciones_sax_{fecha_hoy}.xlsx"
nombre_final = nombre_base
contador = 1
while os.path.exists(nombre_final):
    nombre_final = f"licitaciones_sax_{fecha_hoy}_{contador}.xlsx"
    contador += 1

df_resultado.to_excel(nombre_final, index=False)

# ──────────────── RESUMEN FINAL ──────────────── #

print(f"✅ {len(df_resultado)} licitaciones relevantes encontradas.")
print(f"🚫 {df_filtradas['tiene_excluidas'].sum()} licitaciones descartadas por contener términos excluidos.")
print(f"📁 Archivo guardado: {nombre_final}")
