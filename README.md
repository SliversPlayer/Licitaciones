# 🔎 Licitador - Filtro Inteligente de Licitaciones para Equipamiento Analítico

Este proyecto permite automatizar la búsqueda, descarga y filtrado de licitaciones públicas desde el portal de Mercado Público de Chile, enfocándose en identificar oportunidades relevantes para empresas proveedoras de equipamiento científico y tecnológico, como espectrometría, microscopía y técnicas afines.

## 🚀 Características

- Descarga automática de la base de licitaciones en formato `.zip` desde Mercado Público.
- Extracción y carga del archivo `.xlsx` con Pandas.
- Detección de licitaciones relevantes mediante un conjunto de **palabras clave** configurables.
- Exclusion automática de licitaciones no deseadas mediante una lista de **palabras excluidas**.
- Generación de un archivo Excel con las licitaciones filtradas y normalizadas.
- Sistema de configuración para ajustar el rango de fechas (`dias`) desde un archivo `config.txt`.

## 📁 Estructura del Proyecto
├── licitador.py # Script principal: descarga, filtra y genera el Excel final
├── descargar_y_extraer.py # Función auxiliar para descarga y extracción de ZIP
├── palabras_clave.txt # Lista de palabras clave relevantes
├── palabras_excluidas.txt # Lista de términos excluyentes
├── config.txt # Configuración de parámetros como 'dias'
└── output.xlsx # Archivo generado con las licitaciones relevantes


## ⚙️ Requisitos

- Python 3.8+
- Paquetes:
  - `pandas`
  - `openpyxl`
  - `requests`
  - `tqdm` para barra de progreso.
