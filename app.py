import base64
import glob
import json
import os
import time
from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from googletrans import Translator
from gtts import gTTS
from PIL import Image
import paho.mqtt.client as paho
import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events


def on_publish(client, userdata, result):  # create function for callback
    print("el dato ha sido publicado \n")
    pass


def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.info(f"Respuesta del broker: {message_received}")


broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# --- MEJORA VISUAL: Configuración de la página ---
st.set_page_config(
    page_title="Interfaces Multimodales",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- CABECERA PRINCIPAL ---
st.title("🎙️ INTERFACES MULTIMODALES")
st.subheader("Control por Voz MQTT")
st.markdown("---")

# --- DISEÑO EN COLUMNAS PARA ORDENAR LA IMAGEN Y EL BOTÓN ---
col1, col2 = st.columns([1, 2], gap="medium")

with col1:
    try:
        image = Image.open("voice_ctrl.jpg")
        st.image(image, use_container_width=True)
    except Exception:
        st.info("💡 (Imagen 'voice_ctrl.jpg' no encontrada)")

with col2:
    st.markdown("### Panel de Activación")
    st.write(
        "Toca el botón, concede permisos de micrófono en tu navegador y habla claramente."
    )
    st.markdown("")

    stt_button = Button(label="🎙️ Inicio", width=200)

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
st.markdown("### 📊 Estado y Envío MQTT")

# --- LÓGICA ORIGINAL INTACTA ---
if result:
    if "GET_TEXT" in result:
        st.success(f"Texto reconocido: {result.get('GET_TEXT')}")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass
else:
    st.info("Esperando comando de voz...")
