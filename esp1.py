import machine
import network
import time
import math
from machine import SoftI2C, Pin
from machine import ADC, Pin
from umqtt.simple import MQTTClient
from mpu6050 import MPU6050

# Configuration for I2C
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

# I2C address for MPU6050 for Motor 1
MPU1_ADDR = 0x68

# WiFi credentials
SSID = 'TecNM-ITQuerétaro'
PASSWORD = 'Zorros.ITQ'

# MQTT server configuration
MQTT_SERVER = 'broker.emqx.io'  # Change if needed
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'ESP32_Motor1'
MQTT_USER = 'jair'  # MQTT user
MQTT_PASS = 'ola'    # MQTT passwordS
TOPIC_VIBE_M1 = 'Motor/vibe/M1'
TOPIC_TEMP_M1 = 'Motor/temp/M1'
TOPIC_CONTROL_M1 = 'Motor/control/M1'
TOPIC_CURRENT_M1 = 'Motor/curr/M1'
# Control pin for Motor 1
pin_motor1_control1 = Pin(18, Pin.OUT)
# ADC setup for the current sensor
adc = machine.ADC(machine.Pin(32))  # Adjust the pin as needed
adc.atten(machine.ADC.ATTN_11DB)  # Set ADC attenuation for full range 0-3.3V
adc.width(machine.ADC.WIDTH_12BIT)  # 12-bit resolution (0-4095)

# Function to read current from the SCT013-100 sensor
LOAD_RESISTOR = 33.0  # Ohms (for a 50mA output -> 1V with a 20Ω resistor)
CURRENT_RATIO = 100.0 / 1.0  # 100A per 1V (based on your sensor rating)

# Function to read current from the SCT-013-000 sensor
def read_current_sensor():
    # Read the ADC value (0-4095 for 12-bit resolution)
    sensor_value = adc.read()

    # Convert ADC reading (0-4095) to voltage (0-3.3V range)
    voltaje_sensor = sensor_value * (1.0 / 4095.0)

    # Apply the load resistor and current ratio to calculate current
    corriente = (voltaje_sensor / LOAD_RESISTOR) * CURRENT_RATIO
    corriente *= 10.0
    
    # Print the current value for debugging
    print("Corriente:", corriente, "A")

    # Return the current value
    return corriente

# Function to connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print("\nConnected to WiFi:", wlan.ifconfig())

# Function to publish data to MQTT
def publish_mqtt(client, topic, msg):
    try:
        client.publish(topic, msg)
        print(f"Published to {topic}: {msg}")
    except Exception as e:
        print("Error publishing to MQTT:", e)

# Callback function to handle incoming MQTT messages
def mqtt_callback(topic, msg):
    print("Message received:", topic.decode(), msg.decode())
    # Decode the message from bytes to string for comparison
    decoded_msg = msg.decode()

    # Compare the decoded message with string literals
    if topic == TOPIC_CONTROL_M1.encode():
        if decoded_msg == 'ON':
            pin_motor1_control1.on()
            print("Motor 1 activated")
        elif decoded_msg == 'OFF':
            pin_motor1_control1.off()
            print("Motor 1 deactivated")



# Function to connect to the MQTT broker
def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASS)
        client.set_callback(mqtt_callback)
        print("Connecting to MQTT...")
        client.connect()
        print("Connected to MQTT broker and subscribed to topics")
        client.subscribe(TOPIC_CONTROL_M1)
        return client
    except Exception as e:
        print("Error connecting to MQTT:", e)
        machine.reset()  # Reset ESP32 if connection fails

# Initial setup
def setup():
    connect_wifi()
    print("Waiting to configure MPU6050...")
    time.sleep(1)  # Wait a bit before configuring MPU6050

# Main loop for reading data and publishing to MQTT
RESTING_STATE_OFFSET = 5.0  # Adjust this value based on your actual readings

def loop(client, mpu):
    while True:
        # Read data from MPU6050
        try:
            # Fetch all data: accelerometer and temperature
            accel_x1, accel_y1, accel_z1, temp1 = mpu.get_all_data()
            # print("Raw data from MPU6050: AccX={}, AccY={}, AccZ={}, Temp={}".format(accel_x1, accel_y1, accel_z1, temp1))
        except Exception as e:
            print("Error reading from MPU6050:", e)
            continue  # Skip this iteration if reading fails

        # Add a small threshold to filter noise in accelerometer data
        threshold = 0.05

        # Filter small values to remove noise
        if abs(accel_x1) < threshold:
            accel_x1 = 0
        if abs(accel_y1) < threshold:
            accel_y1 = 0
        if abs(accel_z1) < threshold:
            accel_z1 = 0

        # Scale accelerometer data
        accel_x1 /= 16384.0
        accel_y1 /= 16384.0
        accel_z1 /= 16384.0

        # Calculate the total magnitude of acceleration
        magnitude = math.sqrt(accel_x1**2 + accel_y1**2 + accel_z1**2)
        
        current_m1 = read_current_sensor()

        # Adjust the magnitude by subtracting the offset
        adjusted_magnitude = (magnitude - RESTING_STATE_OFFSET)*-1
        msg_current_m1 = '{:.4f}'.format(current_m1)
        # Ensure the adjusted magnitude does not go below zero
        if adjusted_magnitude < 0:
            adjusted_magnitude = 0

        # Convert temperature to Celsius
        temp_celsius = temp1  # Esto ya está bien si temp1 es en Celsius

        # Create messages for MQTT
        msg_magnitude_m1 = '{:.2f}'.format(adjusted_magnitude)  # Send only the adjusted magnitude
        msg_temp_m1 = '{:.2f}'.format(temp_celsius)
        
        # Debug messages for MQTT data
        print("Adjusted Magnitude data:", msg_magnitude_m1)
        print("Temperature data:", msg_temp_m1)
        print("Current data:", msg_current_m1)

        # Publish adjusted magnitude and temperature data for Motor 1
        publish_mqtt(client, TOPIC_VIBE_M1, msg_magnitude_m1.encode())  # Change this topic if necessary
        publish_mqtt(client, TOPIC_TEMP_M1, msg_temp_m1.encode())
        publish_mqtt(client, TOPIC_CURRENT_M1, msg_current_m1.encode())
        # Check for incoming MQTT messages
        client.check_msg()

        # Sleep between readings
        time.sleep(1)

# Main entry point
if __name__ == "__main__":
    setup()
    client = connect_mqtt()
    mpu = MPU6050(i2c, MPU1_ADDR)
    loop(client, mpu)
