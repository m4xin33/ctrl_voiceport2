import glob
import json
import os
import time
from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from googletrans import Translator
from gtts import gTTS
from openai import OpenAI  # (Mantenemos tus imports originales)
import paho.client as paho  # O paho.mqtt.client según tu entorno
from PIL import Image
import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Control por Voz MQTT",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# --- FUNCIONES MQTT ---
def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.info(f"Mensaje del broker: {message_received}")


broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message


# --- CABECERA PRINCIPAL ---
st.title("🎙️ Interfaces Multimodales: Control por Voz")
st.markdown(
    "Interactúa mediante comandos de voz en tiempo real conectados a un broker MQTT."
)
st.markdown("---")

# --- DISEÑO EN COLUMNAS PARA LA PRESENTACIÓN ---
col1, col2 = st.columns([1, 2], gap="medium")

with col1:
    try:
        image = Image.open("voice_ctrl.jpg")
        st.image(image, use_container_width=True)
    except Exception:
        st.info("💡 [Imagen 'voice_ctrl.jpg' no encontrada]")

with col2:
    st.subheader("Panel de Activación")
    st.markdown(
        "Haz clic en el botón inferior **'Inicio'**, concede permisos de micrófono en tu navegador y pronuncia tu comando."
    )
    st.markdown("")

    # Botón Bokeh para reconocimiento de voz
    stt_button = Button(label="🎤 Iniciar Reconocimiento", width=220)

    stt_button.js_on_event(
        "button_click",
        CustomJS(
            code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
     
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        """
        ),
    )

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0,
    )

st.markdown("---")
st.subheader("📊 Estado y Resultados")

# --- PROCESAMIENTO DEL EVENTO DE VOZ ---
if result:
    if "GET_TEXT" in result:
        texto_reconocido = result.get("GET_TEXT")

        # Mostramos el texto reconocido en una caja bonita de Streamlit
        st.success(f"**Comando detectado:** {texto_reconocido}")

        # Lógica MQTT intacta
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": texto_reconocido.strip()})
        ret = client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except Exception:
        pass
else:
    st.info(
        "Esperando comando de voz... Presiona el botón de arriba y habla claro."
    )
