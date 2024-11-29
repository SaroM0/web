import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
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

conn = st.connection("gsheets", type=GSheetsConnection)

data = conn.read()

def load_client_data_from_google_sheet():
    data = conn.read()
    df = pd.DataFrame(data)
    if 'Solicitud_id' not in df.columns:
        raise ValueError("La columna 'Solicitud_id' no está presente en los datos.")
    client_data_dict = {str(row['Solicitud_id']): row.to_dict() for _, row in df.iterrows()}
    return client_data_dict


def save_to_google_sheet(data, info_worksheet="info", interaction_worksheet="interacciones"):
    try:
        # Convert data to DataFrame
        df = pd.DataFrame([data])

        # Write to the "interacciones" worksheet
        conn.update(
            worksheet=interaction_worksheet,
            data=df
        )

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
        client_data_dict = load_client_data_from_google_sheet()
        client_data = client_data_dict.get(client_id)
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
    image_path = "./images/hombre.png" if gender == "H" else "./images/mujer.png" if gender == "M" else None

    if image_path and os.path.exists(image_path):
        st.image(image_path, width=150, caption="Foto del Cliente")
    else:
        st.error("No se encontró una imagen para el cliente.")

    st.divider()

    mejor_oferta = client_data.get('Mejor Oferta', 'No disponible')

    # Display the 'Mejor Oferta' information
    st.markdown(f"<div class='subtitulo'>Oferta Recomendada: {mejor_oferta}</div>", unsafe_allow_html=True)


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
        if save_to_google_sheet(data_to_save):
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
    image_path = "./images/hombre.png" if gender == "H" else "./images/mujer.png" if gender == "M" else None

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

    # Attempt to retrieve 'Mejor Oferta' from client_data; if it doesn't exist, use 'No disponible' as the default value
    mejor_oferta = client_data.get('Mejor Oferta', 'No disponible')

    # Display the 'Mejor Oferta' information
    st.markdown(f"<div class='subtitulo'>Oferta Recomendada: {mejor_oferta}</div>", unsafe_allow_html=True)

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
        if save_to_google_sheet(data_to_save):
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