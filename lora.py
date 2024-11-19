import network
import time
import ujson
from machine import Pin, ADC, I2C, PWM
from umqtt.simple import MQTTClient
from tflite_runtime.interpreter import Interpreter
import ubinascii

# Wi-Fi Configuration
SSID = 'INFINITUME18B_plus'
PASSWORD = 'cNHkP4gFjT'

# MQTT Configuration
MQTT_SERVER = 'broker.emqx.io'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'ESP32_TrashCan'
TOPIC_ALERT = 'TrashCan/Alert'
TOPIC_DATA = 'TrashCan/Data'
USERNAME = 'jair'
PASSWORD_MQTT = 'ola'

# Sensor Pins
level_sensor = ADC(Pin(32))  # Replace with your ultrasonic sensor pin
weight_sensor = ADC(Pin(33))
odor_sensor = ADC(Pin(34))

# Actuator Pin (Compressor)
compressor = Pin(27, Pin.OUT)

# ML Model Path
MODEL_PATH = 'autoencoder_model.tflite'

# Initialize LoRa (Placeholder for actual LoRa configuration)
# Add LoRa setup code here.

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        time.sleep(1)
    print("Connected to Wi-Fi:", wlan.ifconfig())

# MQTT Setup
def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, port=MQTT_PORT, user=USERNAME, password=PASSWORD_MQTT)
    client.connect()
    print("Connected to MQTT Broker")
    return client

# Initialize TensorFlow Lite Model
def load_model():
    interpreter = Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    return interpreter

# Run ML Inference
def detect_anomaly(interpreter, level, weight, odor):
    # Prepare input data (normalize if necessary)
    sensor_data = [level / 4095, weight / 4095, odor / 4095]  # Scale ADC values to 0-1
    sensor_data = [sensor_data]

    # Set input tensor
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], sensor_data)

    # Run inference
    interpreter.invoke()

    # Get output and compute reconstruction error
    reconstructed_data = interpreter.get_tensor(output_details[0]['index'])
    reconstruction_error = sum((a - b)**2 for a, b in zip(sensor_data[0], reconstructed_data[0]))

    # Threshold for anomaly detection
    if reconstruction_error > 0.05:  # Adjust based on your model
        return True
    return False

# Read Sensor Data
def read_sensors():
    level = level_sensor.read()
    weight = weight_sensor.read()
    odor = odor_sensor.read()
    return level, weight, odor

# Compressor Control
def compress_waste():
    print("Compressing Waste...")
    compressor.value(1)
    time.sleep(2)  # Adjust compression time
    compressor.value(0)

# Send Alerts via LoRa or MQTT
def send_alert(client, message):
    print("Sending Alert:", message)
    client.publish(TOPIC_ALERT, ujson.dumps(message))

# Main Function
def main():
    connect_wifi()
    client = connect_mqtt()
    interpreter = load_model()

    while True:
        try:
            # Read sensors
            level, weight, odor = read_sensors()
            print(f"Level: {level}, Weight: {weight}, Odor: {odor}")

            # Run anomaly detection
            is_anomaly = detect_anomaly(interpreter, level, weight, odor)

            if is_anomaly:
                print("Anomaly Detected!")
                send_alert(client, {"event": "anomaly", "level": level, "weight": weight, "odor": odor})
            else:
                print("Normal Operation")

            # Actuator Logic
            if level > 3000:  # Example threshold for fullness
                compress_waste()

            # Send periodic data update
            data_payload = {"level": level, "weight": weight, "odor": odor, "status": "normal" if not is_anomaly else "anomaly"}
            client.publish(TOPIC_DATA, ujson.dumps(data_payload))

            time.sleep(10)  # Adjust frequency

        except Exception as e:
            print("Error:", str(e))
            time.sleep(5)

# Run the main function
if __name__ == "__main__":
    main()
