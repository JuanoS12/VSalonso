import time
import ujson
from machine import ADC, Pin, UART
from umqtt.simple import MQTTClient
from tflite_runtime.interpreter import Interpreter
import math

# MQTT Configuration
MQTT_SERVER = 'broker.emqx.io'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'ESP32_TrashCan'
TOPIC_PREDICTION = 'TrashCan/Prediction'
USERNAME = 'jair'
PASSWORD_MQTT = 'ola'

# Pins Configuration
level_sensor = ADC(Pin(32))  # Fill level sensor
weight_sensor = ADC(Pin(33))  # Weight sensor
odor_sensor = ADC(Pin(34))  # Odor sensor
gps_uart = UART(1, baudrate=9600, tx=17, rx=16)  # GPS module (pins may vary)

# ML Model Path
MODEL_PATH = 'fill_level_model.tflite'

# Initialize MQTT Client
def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, port=MQTT_PORT, user=USERNAME, password=PASSWORD_MQTT)
    client.connect()
    print("Connected to MQTT Broker")
    return client

# Load TensorFlow Lite Model
def load_model():
    interpreter = Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    return interpreter

# Read GPS Data
def read_gps():
    if gps_uart.any():
        gps_data = gps_uart.readline().decode('utf-8').strip()
        # Example NMEA Sentence Parsing for Latitude/Longitude
        if gps_data.startswith('$GPGGA'):
            parts = gps_data.split(',')
            if len(parts) > 5:
                lat = float(parts[2]) / 100.0
                lon = float(parts[4]) / 100.0
                return {"latitude": lat, "longitude": lon}
    return {"latitude": None, "longitude": None}

# Read Sensor Data with Filtering
def read_sensors():
    # Filter ADC readings with a simple moving average
    def filter_adc(pin, samples=10):
        values = [pin.read() for _ in range(samples)]
        return sum(values) / len(values)

    level = filter_adc(level_sensor)
    weight = filter_adc(weight_sensor)
    odor = filter_adc(odor_sensor)

    # Normalize sensor data (scale to 0-1)
    level = level / 4095
    weight = weight / 4095
    odor = odor / 4095

    return level, weight, odor

# Predict Time to Collect Using ML Model
def predict_time_to_collect(interpreter, level, rate_of_fill):
    # Prepare input
    input_data = [[level, rate_of_fill]]
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # Get prediction
    predicted_time = interpreter.get_tensor(output_details[0]['index'])
    return predicted_time[0]

# Main Function
def main():
    mqtt_client = connect_mqtt()
    interpreter = load_model()

    print("Starting monitoring...")
    previous_level = None
    while True:
        try:
            # Read sensor data
            level, weight, odor = read_sensors()
            gps_data = read_gps()

            # Calculate rate of fill (delta level / time)
            if previous_level is None:
                previous_level = level
                rate_of_fill = 0
            else:
                rate_of_fill = abs(level - previous_level) / 10  # Assuming 10 seconds between measurements
                previous_level = level

            print(f"Level: {level:.2f}, Rate of Fill: {rate_of_fill:.4f}, Weight: {weight:.2f}, Odor: {odor:.2f}")
            print(f"GPS: {gps_data}")

            # Predict time to collect
            predicted_time = predict_time_to_collect(interpreter, level, rate_of_fill)
            print(f"Predicted Time to Collect: {predicted_time:.2f} hours")

            # Publish prediction data
            payload = {
                "level": level,
                "rate_of_fill": rate_of_fill,
                "weight": weight,
                "odor": odor,
                "predicted_time": predicted_time,
                "gps": gps_data
            }
            mqtt_client.publish(TOPIC_PREDICTION, ujson.dumps(payload))
            print("Data published to MQTT.")

            # Wait before next reading
            time.sleep(10)

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

# Run the main loop
if __name__ == "__main__":
    main()
