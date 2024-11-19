from machine import SoftI2C, Pin
import time
from mpu6050 import MPU6050

# Initialize SoftI2C
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))  # Replace 22 and 21 with your actual SCL and SDA pins

# Create MPU6050 object
mpu = MPU6050(i2c)

while True:
    accel_data, temp_data = mpu.get_all_data()
    print("Accelerometer: ax={:.2f}, ay={:.2f}, az={:.2f}".format(*accel_data))
    print("Temperature: {:.2f}°C".format(temp_data))
    time.sleep(1)
