
# Dimex Gestor

**Dimex Gestor** es una aplicación web desarrollada con Streamlit que ayuda a tomar decisiones sobre ofertas de cobranza para clientes, además de proporcionar herramientas para analizar información crediticia.

## Características

- Proporciona recomendaciones de ofertas de cobranza basadas en datos crediticios.
- Integra hojas de cálculo de Google Sheets para gestionar datos en tiempo real.
- Interfaz personalizada con estilos corporativos.
- Fácil despliegue en Streamlit Cloud.

## Requisitos

Para ejecutar la aplicación localmente, asegúrate de instalar las siguientes dependencias:

```
streamlit
pandas
gspread
oauth2client
google-auth
openpyxl
google-cloud-storage
google-cloud-aiplatform
google-cloud-logging
git+https://github.com/streamlit/gsheets-connection
```

Puedes instalar las dependencias ejecutando:

```bash
pip install -r requirements.txt
```

## Instrucciones de Uso

1. Clona este repositorio en tu máquina local.
2. Instala las dependencias mencionadas anteriormente.
3. Ejecuta la aplicación con el siguiente comando:

```bash
streamlit run .streamlit/app.py
```

4. Abre el navegador en la dirección [http://localhost:8501](http://localhost:8501).

## Despliegue en Streamlit Cloud

La aplicación se ha diseñado para su despliegue en Streamlit Cloud. Para desplegar:

1. Sube el repositorio a un servicio como GitHub.
2. Conecta tu cuenta de Streamlit Cloud al repositorio.
3. Configura el archivo `requirements.txt` como lista de dependencias.
4. Especifica `app.py` como el archivo principal.

## Recursos Adicionales

- **Imágenes:** La aplicación incluye recursos gráficos (`hombre.png` y `mujer.png`) para enriquecer la interfaz.
- **Script auxiliar:** Un script de inicialización (`run.sh`) puede ser útil para despliegues en entornos personalizados.


## El proyecto se encuentra diponible en streamlit cloud bajo el sieguiente link:


https://equipo3-web.streamlit.app/

## El repo
https://github.com/SaroM0/web
