import network
import time
import ujson
from machine import Pin, SPI, ADC, PWM, I2C
from umqtt.simple import MQTTClient
from sx127x import SX127x
import numpy as np
import tflite_runtime.interpreter as tflite
# Wi-Fi Configuration
SSID = 'INFINITUME18B_plus'
PASSWORD = 'cNHkP4gFjT'

# MQTT Configuration
MQTT_SERVER = 'broker.emqx.io'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'ESP32_SmartTrash'
TOPIC_NUMERIC = 'TrashCan/Numeric'
USERNAME = 'jair'
PASSWORD_MQTT = 'ola'

# LoRa Configuration
SPI_BUS = SPI(1, baudrate=10000000, polarity=0, phase=0)
CS_PIN = 5      # Chip Select Pin
RESET_PIN = 18  # Reset Pin
IRQ_PIN = 26    # IRQ Pin
LORA_FREQ = 915e6

# Sensor/Actuator Pins
LEVEL_SENSOR_TRIG_PIN = 25    # Ultrasonic Sensor Trigger Pin
LEVEL_SENSOR_ECHO_PIN = 26    # Ultrasonic Sensor Echo Pin
WEIGHT_SENSOR_PIN = 39        # Analog Pin for Weight Sensor
ODOR_SENSOR_PIN = 34          # Analog Pin for Odor Sensor
TEMP_SENSOR_PIN = 35          # Analog Pin for Temperature Sensor
GPS_TX_PIN = 17               # GPS Module TX Pin
GPS_RX_PIN = 16               # GPS Module RX Pin
ACTUATOR_PWM_PIN = 22         # PWM pin for actuator motor

# Initialize Components
lora = SX127x(SPI_BUS, CS_PIN, RESET_PIN, IRQ_PIN)
level_sensor = ADC(Pin(LEVEL_SENSOR_PIN))
weight_sensor = ADC(Pin(WEIGHT_SENSOR_PIN))
odor_sensor = ADC(Pin(ODOR_SENSOR_PIN))
temp_sensor = ADC(Pin(TEMP_SENSOR_PIN))
actuator = PWM(Pin(ACTUATOR_PWM_PIN), freq=50)  # Actuator control (e.g., servo)
gps_uart = machine.UART(GPS_UART_PORT, baudrate=9600)

# --- TensorFlow Lite Model Setup ---
model_path = "anti_theft_model.tflite"  # Path to the TFLite model file
interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get input and output details from the model
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Wi-Fi Connection
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        time.sleep(1)
    print("Connected to Wi-Fi:", wlan.ifconfig())

# MQTT Connection
def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, port=MQTT_PORT, user=USERNAME, password=PASSWORD_MQTT)
    client.connect()
    print("Connected to MQTT Broker")
    return client

# Read Sensors
def read_sensors():
    # Read level sensor (ultrasonic distance, normalized)
    level = level_sensor.read() / 4095 * 100  # Example percentage
    # Read weight sensor (normalized to kg)
    weight = weight_sensor.read() / 4095 * 50  # Example range: 0–50 kg
    # Read odor sensor (normalized)
    odor = odor_sensor.read() / 4095 * 100  # Example percentage
    # Read temperature sensor (converted to Celsius)
    temp = temp_sensor.read() / 4095 * 50  # Example range: 0–50°C

    # Read GPS data
    gps_data = gps_uart.readline()  # Raw GPS NMEA sentence
    if gps_data:
        gps_data = gps_data.decode('utf-8').strip()
    else:
        gps_data = "No GPS Data"

    return {
        "level": level,
        "weight": weight,
        "odor": odor,
        "temp": temp,
        "gps": gps_data
    }

# Actuator Control
def compress_waste():
    print("Activating actuator to compress waste...")
    actuator.duty(50)  # Example PWM duty cycle for compression
    time.sleep(5)  # Compression duration
    actuator.duty(0)  # Stop actuator
    print("Compression complete")

# LoRa Send
def send_string_lora(data):
    lora.set_frequency(LORA_FREQ)
    lora.send(data.encode('utf-8'))
    print(f"String data sent via LoRa: {data}")

# MQTT Send
def send_numeric_mqtt(client, data):
    payload = ujson.dumps(data)
    client.publish(TOPIC_NUMERIC, payload)
    print(f"Numeric data sent via MQTT: {payload}")

# Main Function
def main():
    connect_wifi()
    mqtt_client = connect_mqtt()

    while True:
        try:
            # Read sensors
            sensor_data = read_sensors()

            # Log data
            print("Sensor Data:", sensor_data)

            # Check if waste needs compression (e.g., level > 80%)
            if sensor_data['level'] > 80:
                compress_waste()

            # Send numeric data via MQTT
            numeric_data = {key: val for key, val in sensor_data.items() if key != "gps"}
            send_numeric_mqtt(mqtt_client, numeric_data)

            # Send GPS data (or other strings) via LoRa
            send_string_lora(sensor_data['gps'])

            time.sleep(10)  # Adjust interval as needed

        except Exception as e:
            print("Error:", str(e))
            time.sleep(5)

# Run Main
if __name__ == "__main__":
    main()
