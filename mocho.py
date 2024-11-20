import time
import uos
from machine import ADC, Pin, UART
import ubinascii

# Configuración de sensores
level_sensor = ADC(Pin(32))
weight_sensor = ADC(Pin(33))
odor_sensor = ADC(Pin(34))

level_sensor.atten(ADC.ATTN_11DB)  # Rango 0-3.3V
weight_sensor.atten(ADC.ATTN_11DB)
odor_sensor.atten(ADC.ATTN_11DB)

# Configuración de GPS
uart_gps = UART(1, baudrate=9600, tx=17, rx=16)  # Pines UART TX=17, RX=16

# Crear archivo CSV
filename = "sensor_data.csv"

def init_file():
    try:
        with open(filename, "w") as file:
            file.write("timestamp,level,weight,odor,latitude,longitude,speed\n")
        print(f"Archivo {filename} creado exitosamente.")
    except Exception as e:
        print("Error al crear el archivo:", e)

# Leer datos del GPS
def read_gps():
    if uart_gps.any():
        data = uart_gps.readline().decode("utf-8", errors="ignore")
        if data.startswith("$GNRMC"):  # Usamos el mensaje RMC (velocidad y posición)
            parts = data.split(",")
            if parts[3] and parts[5] and parts[7]:  # Latitud, longitud, velocidad
                try:
                    lat = float(parts[3])
                    lat_dir = parts[4]
                    lon = float(parts[5])
                    lon_dir = parts[6]
                    speed = float(parts[7])  # Velocidad en nudos

                    # Convertir latitud y longitud a decimal
                    latitude = (lat // 100) + (lat % 100) / 60
                    longitude = (lon // 100) + (lon % 100) / 60
                    if lat_dir == "S":
                        latitude = -latitude
                    if lon_dir == "W":
                        longitude = -longitude

                    # Convertir velocidad de nudos a km/h
                    speed_kmh = speed * 1.852
                    return latitude, longitude, speed_kmh
                except ValueError:
                    return None, None, None
    return None, None, None

# Leer datos de los sensores
def read_sensors():
    level = level_sensor.read()
    weight = weight_sensor.read()
    odor = odor_sensor.read()
    return level, weight, odor

# Guardar datos en el archivo
def save_data(level, weight, odor, latitude, longitude, speed):
    try:
        with open(filename, "a") as file:
            timestamp = time.time()
            file.write(f"{timestamp},{level},{weight},{odor},{latitude},{longitude},{speed}\n")
        print("Datos guardados:", level, weight, odor, latitude, longitude, speed)
    except Exception as e:
        print("Error al guardar datos:", e)

# Bucle principal
def main():
    init_file()
    while True:
        try:
            # Leer sensores
            level, weight, odor = read_sensors()

            # Leer GPS
            latitude, longitude, speed = read_gps()
            if latitude is None or longitude is None or speed is None:
                latitude, longitude, speed = "N/A", "N/A", "N/A"

            # Guardar datos
            save_data(level, weight, odor, latitude, longitude, speed)

            # Esperar antes de la próxima lectura
            time.sleep(5)  # Ajustar intervalo según sea necesario
        except Exception as e:
            print("Error en el bucle principal:", e)
            time.sleep(5)

# Ejecutar el script
if __name__ == "__main__":
    main()
