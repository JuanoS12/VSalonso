import network
import time
from umqtt.simple import MQTTClient

# Configuración WiFi
SSID = 'INFINITUME18B_plus'
PASSWORD = 'cNHkP4gFjT'

# Datos del servidor MQTT
MQTT_SERVER = 'broker.emqx.io'  # Cambia a la dirección IP local de tu computadora
MQTT_PORT = 1883  # Puerto del broker
MQTT_CLIENT_ID = 'ESP32_Test'
TOPIC_TEST = 'Test/Topic'
USERNAME = 'jair'  # Usuario de MQTT
PASSWORD_MQTT = 'ola'  # Contraseña de MQTT

# Conectar al WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Conectando a WiFi...")
        time.sleep(1)
    print("Conectado a WiFi:", wlan.ifconfig())

# Publicar un mensaje
def publish_mqtt(client):
    try:
        client.publish(TOPIC_TEST, b'Test message from ESP32')
        print("Mensaje publicado en el tópico:", TOPIC_TEST)
    except OSError as e:
        print("Error publicando mensaje:", e)

# Código principal
def main():
    connect_wifi()
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, MQTT_PORT, USERNAME, PASSWORD_MQTT)
        client.connect()
        print("Conectado al broker MQTT")
        publish_mqtt(client)
    except OSError as e:
        print("Error conectando al broker MQTT:", e)

# Ejecutar el código principal
main()
