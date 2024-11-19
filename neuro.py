from machine import I2C, Pin
import math
import time
import random
import ustruct

# Configuración de I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Dirección del MPU6050
MPU6050_ADDR = 0x68

# Inicialización del MPU6050
def init_mpu6050():
    i2c.writeto_mem(MPU6050_ADDR, 0x6B, b'\x00')  # Despertar el MPU6050

# Lectura de datos de aceleración y giroscopio
def leer_datos():
    try:
        data = i2c.readfrom_mem(MPU6050_ADDR, 0x3B, 14)
        accel_x = ustruct.unpack('>h', data[0:2])[0]
        accel_y = ustruct.unpack('>h', data[2:4])[0]
        accel_z = ustruct.unpack('>h', data[4:6])[0]
        gyro_x = ustruct.unpack('>h', data[8:10])[0]
        gyro_y = ustruct.unpack('>h', data[10:12])[0]
        gyro_z = ustruct.unpack('>h', data[12:14])[0]
        return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
    except Exception as e:
        print("Error al leer datos:", e)
        return None

# Función de activación Sigmoid
def sigmoid(x):
    if x < -709:
        return 0.0
    elif x > 709:
        return 1.0
    return 1 / (1 + math.exp(-x))

# Inicialización de la red neuronal
def inicializar_pesos():
    return [random.uniform(-1, 1) for _ in range(6)]

# Función para calcular la salida de la red
def salida_red(datos, pesos):
    suma = sum(d * p for d, p in zip(datos, pesos))
    print("Suma:", suma)  # Para depuración
    return sigmoid(suma)

# Función de entrenamiento
def entrenar_red(pesos, datos_entrada, salida_deseada, tasa_aprendizaje=0.9):
    salida = salida_red(datos_entrada, pesos)
    error = salida_deseada - salida
    for i in range(len(pesos)):
        pesos[i] += tasa_aprendizaje * error * datos_entrada[i]
    return pesos, error

# Función para recolectar datos
def recolectar_datos(gesto, cantidad_muestras):
    datos_gesto = []
    for _ in range(cantidad_muestras):
        datos = leer_datos()
        if datos:
            datos_gesto.append(datos)
        time.sleep(0.1)  # Pequeño retardo para tomar muestras
    return datos_gesto

# Inicializa el sensor y la red
init_mpu6050()
pesos_izquierda = inicializar_pesos()
pesos_derecha = inicializar_pesos()

# Fase de entrenamiento
cantidad_muestras = 100
for _ in range(2):  # Entrenar por x ciclos
    # Recolecta datos para el gesto "derecha"
    print("Realiza el gesto 'derecha'")
    muestras_derecha = recolectar_datos('derecha', cantidad_muestras)
    for muestra in muestras_derecha:
        pesos_derecha, error_derecha = entrenar_red(pesos_derecha, muestra, 1)

    # Recolecta datos para el gesto "izquierda"
    print("Realiza el gesto 'izquierda'")
    muestras_izquierda = recolectar_datos('izquierda', cantidad_muestras)
    for muestra in muestras_izquierda:
        pesos_izquierda, error_izquierda = entrenar_red(pesos_izquierda, muestra, 0)

# Imprime los pesos finales
print("Pesos finales para 'derecha':", pesos_derecha)
print("Pesos finales para 'izquierda':", pesos_izquierda)

# Fase de reconocimiento
def reconocer_gesto():
    datos_actuales = leer_datos()
    if datos_actuales:
        salida_izquierda = salida_red(datos_actuales, pesos_izquierda)
        salida_derecha = salida_red(datos_actuales, pesos_derecha)

        if salida_izquierda > 0.3:
            return "izquierda", datos_actuales, salida_izquierda
        elif salida_derecha > 0.7:
            return "derecha", datos_actuales, salida_derecha
        else:
            return "gesto desconocido", datos_actuales, None
    return "error en la lectura", None, None

# Reconocimiento en bucle
while True:
    gesto, coordenadas, salida = reconocer_gesto()
    print("Gesto reconocido:", gesto)
    if coordenadas:
        print("Coordenadas MPU:", coordenadas)
        if salida is not None:
            print("Salida de la red:", salida)
    time.sleep(1)  # Pequeño retardo antes de la siguiente iteración
