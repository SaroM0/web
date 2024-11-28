import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import os

# Configuración de la página
st.set_page_config(page_title="Dimex Gestor", page_icon=":office:", layout="centered")
 
# Estilo global con los colores personalizados
st.markdown(
    """
    <style>
    .titulo {
        color: #4B4F54;
        font-size: 28px;
        font-weight: bold;
    }
    .subtitulo {
        color: #63A532;
        font-size: 22px;
        font-weight: bold;
    }
    .texto-destacado {
        color: #4B4F54;
        font-size: 16px;
        font-weight: bold;
    }
    .texto-normal {
        color: #4B4F54;
        font-size: 14px;
    }
    .caption {
        color: #4B4F54;
        font-size: 12px;
        font-style: italic;
    }
    .slider-container {
        position: relative;
        width: 100%;
        height: 20px;
        margin-top: 10px;
    }
    .slider-bar {
        height: 20px;
        border-radius: 10px;
    }
    .slider-value {
        position: absolute;
        top: -25px;
        right: 0;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Configuración
json_keyfile = './data/webxd-443102-7fed334fecbf.json'
sheet_url = 'https://docs.google.com/spreadsheets/d/1IQkWouB4WKuSyAW5zy6jRDJpJ3VuMRbKY8MIrrOV7A0/edit?gid=924511829#gid=924511829'
sheet_name = 'info'

def load_client_data_from_google_sheet(json_keyfile, sheet_url, sheet_name):
        # Definir el alcance y autorizar con las credenciales
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
        client = gspread.authorize(creds)

        # Abrir el archivo de Google Sheets
        spreadsheet = client.open_by_url(sheet_url)
        sheet = spreadsheet.worksheet(sheet_name)

        # Obtener todos los registros
        records = sheet.get_all_records()

        # Convertir los datos a un DataFrame de pandas
        df = pd.DataFrame(records)

        # Validar la columna 'Solicitud_id'
        if 'Solicitud_id' not in df.columns:
            raise ValueError("La columna 'Solicitud_id' no está presente en los datos.")

        # Convertir a un diccionario usando 'Solicitud_id' como clave
        client_data_dict = {str(row['Solicitud_id']): row.to_dict() for _, row in df.iterrows()}

        return client_data_dict

# Función para guardar datos en Excel
def save_to_google_sheet(data, json_keyfile, sheet_url, sheet_name, interaction_sheet_name="interacciones"):
    try:
        # Definir el alcance y autorizar con las credenciales
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(json_keyfile, scopes=scope)
        client = gspread.authorize(creds)

        # Abrir el archivo de Google Sheets
        spreadsheet = client.open_by_url(sheet_url)

        # Trabajar con la hoja principal
        sheet = spreadsheet.worksheet(sheet_name)
        existing_records = sheet.get_all_records()
        df = pd.DataFrame(existing_records)

        # Si la hoja está vacía, crea un DataFrame con las columnas iniciales
        if df.empty:
            df = pd.DataFrame(columns=["ID del Cliente", "Decisión", "Promesa de Pago (Fecha)", "Promesa de Pago (Monto)", "Comentarios"])

        # Convertir objetos de tipo fecha a cadenas y manejar valores nulos
        for key, value in data.items():
            if isinstance(value, (datetime, date)):
                data[key] = value.strftime('%Y-%m-%d')
            elif value is None:
                data[key] = ""  # Reemplazar valores nulos con cadenas vacías

        # Comprobar si el ID del Cliente ya existe en los registros
        if "ID del Cliente" in df.columns and str(data["ID del Cliente"]) in df["ID del Cliente"].astype(str).values:
            # Actualizar el registro existente
            idx = df.index[df["ID del Cliente"].astype(str) == str(data["ID del Cliente"])].tolist()[0]
            for key, value in data.items():
                df.at[idx, key] = value
            print(f"Registro actualizado para el ID del Cliente: {data['ID del Cliente']}")
        else:
            # Añadir el nuevo registro al DataFrame
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            print(f"Nuevo registro añadido para el ID del Cliente: {data['ID del Cliente']}")

        # Reemplazar valores NaN por cadenas vacías para compatibilidad con JSON
        df = df.fillna("")

        # Sobrescribir los datos en la hoja principal
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

        # Trabajar con la hoja de interacciones
        interaction_sheet = spreadsheet.worksheet(interaction_sheet_name)
        interaction_records = interaction_sheet.get_all_records()
        interaction_df = pd.DataFrame(interaction_records)

        # Si la hoja de interacciones está vacía, crea un DataFrame con las columnas iniciales
        if interaction_df.empty:
            interaction_df = pd.DataFrame(columns=[
                "ID del Cliente", "Decisión", "Fecha de Interacción", "Monto", "Comentarios"
            ])

        # Agregar los datos relevantes a la hoja de interacciones
        interaction_data = {
            "ID del Cliente": data["ID del Cliente"],
            "Decisión": data["Decisión"],
            "Fecha de Interacción": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Fecha actual
            "Monto": data.get("Promesa de Pago (Monto)", ""),
            "Comentarios": data.get("Comentarios", "")
        }
        interaction_df = pd.concat([interaction_df, pd.DataFrame([interaction_data])], ignore_index=True)

        # Reemplazar valores NaN por cadenas vacías para compatibilidad con JSON
        interaction_df = interaction_df.fillna("")

        # Sobrescribir los datos en la hoja de interacciones
        interaction_sheet.update([interaction_df.columns.values.tolist()] + interaction_df.values.tolist())

        return True
    except Exception as e:
        print(f"Error al guardar o actualizar los datos: {e}")
        return False

# Pantalla de inicio de sesión
def login_screen():
    st.markdown("<div class='titulo'>Bienvenido al Sistema de Gestión - Dimex</div>", unsafe_allow_html=True)
    username = st.text_input("Usuario:", placeholder="Ingresa tu usuario")
    password = st.text_input("Contraseña:", type="password", placeholder="Ingresa tu contraseña")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Call Center"):
            if username == "callcenter" and password == "dimex123":
                st.session_state["logged_in"] = True
                st.session_state["role"] = "call_center"
                st.session_state["page"] = "enter_id"
            else:
                st.error("Usuario o contraseña incorrectos.")
    with col2:
        if st.button("Gestor de Cobranza"):
            if username == "gestor" and password == "dimex123":
                st.session_state["logged_in"] = True
                st.session_state["role"] = "gestor"
                st.session_state["page"] = "enter_id"
            else:
                st.error("Usuario o contraseña incorrectos.")

# Pantalla para ingresar el ID del cliente
#puedes agregar un boton para volver a la pantalla de iniciar sesion
def enter_id_screen():
    st.markdown("<div class='titulo'>Consulta de Cliente</div>", unsafe_allow_html=True)
    client_id = st.text_input("Ingresa el ID del cliente:", placeholder="Ejemplo: 12345")
    if st.button("Buscar Cliente"):
        client_data = client_data = load_client_data_from_google_sheet(json_keyfile, sheet_url, sheet_name).get(client_id)
        if client_data:
            st.session_state["client_data"] = client_data
            st.session_state["page"] = st.session_state["role"]
        else:
            st.error("Cliente no encontrado.")

    # Botón para regresar a la pantalla de inicio de sesión
    if st.button("Cerrar sesión"):
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"


# Pantalla de Call Center
def call_center_screen():
    client_data = st.session_state.get("client_data", {})
    if not client_data:
        st.warning("No se encontró información del cliente.")
        return

    # Mostrar detalles del cliente
    st.markdown(f"<div class='titulo'>ID: {client_data['Solicitud_id']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='caption'>{client_data.get('Nombre', 'Nombre no disponible')}</div>", unsafe_allow_html=True)

    # Mostrar imagen según el género
    gender = client_data.get("Genero", "").upper()
    image_path = "hombre.png" if gender == "H" else "mujer.png" if gender == "M" else None

    if image_path and os.path.exists(image_path):
        st.image(image_path, width=150, caption="Foto del Cliente")
    else:
        st.error("No se encontró una imagen para el cliente.")

    st.divider()

    st.markdown(f"<div class='subtitulo'>Oferta Recomendada: {client_data['Mejor Oferta']}</div>", unsafe_allow_html=True)

    st.divider()

    # Decisión del Call Center
    st.markdown("<div class='subtitulo'>Decisión del Gestor</div>", unsafe_allow_html=True)
    decision = st.selectbox("Selecciona una opción:", ["Quita/Castigo", "Tus Pesos Valen Más", "Pago Sin Beneficio", "Reestructura del Crédito"])
    
    incluir_promesa = st.checkbox("¿Registrar una promesa de pago?")
    promise_date = None
    promise_amount = None
    if incluir_promesa:
        promise_date = st.date_input("Fecha de promesa de pago:")
        promise_amount = st.number_input("Monto prometido ($):", min_value=0.0, step=100.0)

    comentarios = st.text_area("Comentarios:", placeholder="Escribe aquí tus comentarios...")

    if st.button("Guardar Información"):
        # Preparar datos para guardar
        data_to_save = {
            "ID del Cliente": client_data["Solicitud_id"],
            "Decisión": decision,
            "Promesa de Pago (Fecha)": promise_date if incluir_promesa else None,
            "Promesa de Pago (Monto)": promise_amount if incluir_promesa else None,
            "Comentarios": comentarios,
        }

        # Guardar en Excel
        if save_to_google_sheet(data_to_save, json_keyfile, sheet_url, sheet_name):
            st.success("Información guardada correctamente.")
        else:
            st.error("No se pudo guardar la información.")

    if st.button("Regresar"):
        st.session_state["page"] = "enter_id"





# Pantalla de Gestor de Cobranza
def gestor_screen():
    client_data = st.session_state.get("client_data", {})
    if not client_data:
        st.warning("No se encontró información del cliente.")
        return

    # Mostrar detalles del cliente
    st.markdown(f"<div class='titulo'>ID: {client_data['Solicitud_id']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='caption'>{client_data.get('Nombre', 'Nombre no disponible')}</div>", unsafe_allow_html=True)

    # Mostrar imagen según el género
    gender = client_data.get("Genero", "").upper()
    image_path = "hombre.png" if gender == "H" else "mujer.png" if gender == "M" else None

    if image_path and os.path.exists(image_path):
        st.image(image_path, width=150, caption="Foto del Cliente")
    else:
        st.error("No se encontró una imagen para el cliente.")

    st.divider()

    # Métricas principales
    st.markdown("<div class='subtitulo'>Detalles del Cliente</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Ingreso Bruto", f"${client_data.get('Ingreso_Bruto', 0):,}")
    col2.metric("Edad", f"{client_data.get('Edad', 'N/A')} años")
    col3.metric("Saldo Actual", f"${client_data.get('Deuda Acumulada', 0):,}")

    st.divider()

    # Nivel de atraso con colores personalizados
    st.markdown("<div class='subtitulo'>Nivel de Atraso</div>", unsafe_allow_html=True)
    atraso_niveles = {
        "1_29": 10,
        "30_59": 40,
        "60_89": 70,
        "90_119": 85,
        "120_149": 95,
        "150_179": 100,
    }
    nivel_atraso = client_data.get("Nivel de Atraso", "").strip()
    progreso = atraso_niveles.get(nivel_atraso)

    if progreso is not None:
        color = (
            "#63A532" if progreso <= 25 else  # Verde fuerte
            "#A8D08D" if progreso <= 50 else  # Verde claro
            "#FFD966" if progreso <= 75 else  # Amarillo
            "#E06666"  # Naranja
        )
        st.markdown(f"<div class='texto-destacado'>Nivel de Atraso: {nivel_atraso}</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="slider-container">
                <div class="slider-bar" style="background: linear-gradient(90deg, {color} {progreso}%, #ddd {progreso}%);"></div>
                <div class="slider-value">{progreso}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning(f"Nivel de atraso desconocido: {nivel_atraso}. No se puede mostrar el slider.")

    st.divider()

    st.markdown(f"<div class='subtitulo'>Oferta Recomendada: {client_data['Mejor Oferta']}</div>", unsafe_allow_html=True)

    st.divider()

    # Decisión del Gestor
    st.markdown("<div class='subtitulo'>Decisión del Gestor</div>", unsafe_allow_html=True)
    decision = st.selectbox("Selecciona una opción:", ["Quita/Castigo", "Tus Pesos Valen Más", "Pago Sin Beneficio", "Reestructura del Crédito"])
    
    incluir_promesa = st.checkbox("¿Registrar una promesa de pago?")
    promise_date = None
    promise_amount = None
    if incluir_promesa:
        promise_date = st.date_input("Fecha de promesa de pago:")
        promise_amount = st.number_input("Monto prometido ($):", min_value=0.0, step=100.0)
    comentarios = st.text_area("Comentarios:", placeholder="Escribe aquí tus comentarios...")

    if st.button("Guardar Información"):
        # Preparar datos para guardar
        data_to_save = {
            "ID del Cliente": client_data["Solicitud_id"],
            "Decisión": decision,
            "Promesa de Pago (Fecha)": promise_date if incluir_promesa else None,
            "Promesa de Pago (Monto)": promise_amount if incluir_promesa else None,
            "Comentarios": comentarios or "",
        }

        # Guardar en Excel
        if save_to_google_sheet(data_to_save, json_keyfile, sheet_url, sheet_name):
            st.success("Información guardada correctamente.")
        else:
            st.error("No se pudo guardar la información.")

    if st.button("Regresar"):
        st.session_state["page"] = "enter_id"

# Control de flujo de la aplicación
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["page"] = "login"

if st.session_state["page"] == "login":
    login_screen()
elif st.session_state["page"] == "enter_id":
    enter_id_screen()
elif st.session_state["page"] == "call_center":
    call_center_screen()
elif st.session_state["page"] == "gestor":
    gestor_screen()
 ## C:\Users\karen\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\streamlit.exe run app.py