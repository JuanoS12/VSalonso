from machine import I2C, Pin
import time

class MPU6050:
    def __init__(self, scl_pin, sda_pin):
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.address = 0x68  # Dirección del MPU6050
        self.init_sensor()

    def init_sensor(self):
        self.i2c.writeto(self.address, bytearray([0x6B, 0]))  # Despertar el sensor

    def leer_datos(self):
        # Leer los registros de aceleración y giroscopio
        data = self.i2c.readfrom_mem(self.address, 0x3B, 14)
        accel_x = (data[0] << 8) | data[1]
        accel_y = (data[2] << 8) | data[3]
        accel_z = (data[4] << 8) | data[5]
        gyro_x = (data[8] << 8) | data[9]
        gyro_y = (data[10] << 8) | data[11]
        gyro_z = (data[12] << 8) | data[13]

        # Convertir a G y grados por segundo
        accel_x /= 16384.0
        accel_y /= 16384.0
        accel_z /= 16384.0
        gyro_x /= 131.0
        gyro_y /= 131.0
        gyro_z /= 131.0

        # Mostrar datos
       # print(f"Aceleración: X={accel_x:.2f}, Y={accel_y:.2f}, Z={accel_z:.2f}")
       # print(f"Giroscopio: X={gyro_x:.2f}, Y={gyro_y:.2f}, Z={gyro_z:.2f}")

        return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

# Prueba del sensor
mpu = MPU6050(scl_pin=22, sda_pin=21)
while True:
    mpu.leer_datos()
    time.sleep(1)
