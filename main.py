from machine import I2C, Pin
import time
from red_neuronal import RedNeuronal

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

        # Mostrar datos del sensor
        print(f"Aceleración: X={accel_x:.2f}, Y={accel_y:.2f}, Z={accel_z:.2f}")
        print(f"Giroscopio: X={gyro_x:.2f}, Y={gyro_y:.2f}, Z={gyro_z:.2f}")

        return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

# Configuración del MPU6050
mpu = MPU6050(scl_pin=22, sda_pin=21)

# Definición de parámetros para la red neuronal
entradas = 6  # Aceleración y giroscopio
neuronas_ocultas = 5
salidas = 2  # Número de gestos
red_neuronal = RedNeuronal(entradas, neuronas_ocultas, salidas)

# Recolección de datos
gestos = ['izquierda', 'derecha']
datos_entradas = []
datos_salidas = []

for gesto in gestos:
    input(f"Comienza el gesto: {gesto}")
    for _ in range(20):  # Recolectar 20 muestras por gesto
        accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = mpu.leer_datos()
        datos_entradas.append([accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z])
        datos_salidas.append([1 if g == gesto else 0 for g in gestos])
        time.sleep(0.1)

# Entrenamiento de la red
red_neuronal.entrenar(datos_entradas, datos_salidas, epochs=100)

# Mostrar pesos de las neuronas después del entrenamiento
for i, neurona in enumerate(red_neuronal.neuronas):
    print(f"Pesos de la neurona oculta {i}: {neurona.pesos}")
for i, neurona in enumerate(red_neuronal.salidas):
    print(f"Pesos de la neurona de salida {i}: {neurona.pesos}")

# Ejemplo de clasificación
while True:
    accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = mpu.leer_datos()
    entrada_actual = [accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z]
    
    ocultas = [neurona.activar(entrada_actual) for neurona in red_neuronal.neuronas]
    salida = [neurona.activar(ocultas) for neurona in red_neuronal.salidas]
  
    gesto_predicho = gestos[salida.index(max(salida))]
    print(f"Gesto predicho: {gesto_predicho}")
    
    time.sleep(1)

