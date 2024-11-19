from machine import Pin
from time import sleep

# Define los pines de los LEDs de la ESP32 LoRaWAN
led_pins = [Pin(25, Pin.OUT),  # LED1
            Pin(26, Pin.OUT),  # LED2
            Pin(27, Pin.OUT)]  # LED3

# Función para encender los LEDs en secuencia
def led_sequence(delay=0.5):
    while True:
        for led in led_pins:
            led.on()      # Enciende el LED
            sleep(delay)  # Espera un tiempo
            led.off()     # Apaga el LED

# Ejecuta la secuencia de LEDs
led_sequence()
