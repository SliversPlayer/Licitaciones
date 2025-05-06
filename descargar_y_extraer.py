import os
import requests
import zipfile

def descargar_y_extraer_xlsx(url_zip: str) -> str:
    """
    Descarga un ZIP desde la URL, lo guarda en el directorio actual,
    extrae el primer archivo .xlsx encontrado en el ZIP en el mismo lugar,
    y retorna la ruta completa del .xlsx extraído.
    """
    # Directorio actual
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))

    # Definir nombres de archivos
    nombre_zip = os.path.join(carpeta_actual, "licitaciones.zip")

    # Descargar ZIP
    print("⬇️ Descargando archivo ZIP...")
    response = requests.get(url_zip)
    response.raise_for_status()

    # Guardar ZIP en el mismo directorio
    with open(nombre_zip, "wb") as f:
        f.write(response.content)
    print(f"✅ ZIP guardado en: {nombre_zip}")

    # Abrir y extraer el primer archivo .xlsx
    with zipfile.ZipFile(nombre_zip, "r") as zip_ref:
        archivos = zip_ref.namelist()
        archivos_xlsx = [f for f in archivos if f.endswith(".xlsx")]

        if not archivos_xlsx:
            raise Exception("❌ No se encontró ningún archivo .xlsx en el ZIP.")

        archivo_xlsx = archivos_xlsx[0]
        zip_ref.extract(archivo_xlsx, carpeta_actual)

    ruta_xlsx_extraido = os.path.join(carpeta_actual, archivo_xlsx)

    print(f"✅ XLSX extraído en: {ruta_xlsx_extraido}")
    return ruta_xlsx_extraido
