from machine import ADC, Pin, PWM
import time
import math

# Constantes
LEARNING_RATE = 0.95

# Pesos iniciales de la red neuronal
weights_hidden = [[-0.1], [-0.11], [-0.12]]
weights_output = [0.1, -0.17, 0.19]

# Configuración del ADC
adc0 = ADC(Pin(36))  # Setpoint (Entrada analógica 1)
adc1 = ADC(Pin(39))  # Salida (Entrada analógica 2)

# Configuración del PWM en el pin 2 (ajustable)
pwm = PWM(Pin(2), freq=5000, duty=0)

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def sigmoid_derivative(x):
    sig = sigmoid(x)
    return sig * (1 - sig)

def read_analog(adc):
    return adc.read() / 4095.0  # Normalización a 0-1 (resolución de 12 bits)

while True:
    # Leer el setpoint y la salida
    setpoint = read_analog(adc0)
    output = read_analog(adc1)

    # Calcular el error
    error = setpoint - output

    # Calcular salidas de las neuronas ocultas y actualizar pesos
    hidden_outputs = []
    for i in range(3):
        net_input_hidden = weights_hidden[i][0] * setpoint
        hidden_output = sigmoid(net_input_hidden)
        hidden_outputs.append(hidden_output)

        # Actualizar pesos de las neuronas ocultas
        delta_hidden = LEARNING_RATE * error * sigmoid_derivative(net_input_hidden) * weights_output[i] * sigmoid_derivative(net_input_hidden)
        weights_hidden[i][0] += delta_hidden * setpoint

    # Calcular salida de la neurona de salida
    net_input_output = sum(hidden_outputs[i] * weights_output[i] for i in range(3))
    output_neuron = sigmoid(net_input_output)

    # Actualizar pesos de la neurona de salida
    delta_output = LEARNING_RATE * error * sigmoid_derivative(net_input_output)
    for i in range(3):
        weights_output[i] += delta_output * hidden_outputs[i]

    # Generar señal PWM
    pwm_value = int(output_neuron * 1023)  # Escala a 10 bits para PWM en ESP32
    pwm_value = max(0, min(pwm_value, 1023))  # Limitar entre 0 y 1023
    pwm.duty(pwm_value)

    # Mostrar los valores actuales
    print(f"Setpoint: {setpoint:.2f}, Output: {output:.2f}")
    print(f"Pesos ocultos: {weights_hidden[0][0]:.2f}, {weights_hidden[1][0]:.2f}, {weights_hidden[2][0]:.2f}")
    print(f"Pesos salida: {weights_output[0]:.2f}, {weights_output[1]:.2f}, {weights_output[2]:.2f}")

    # Pausa
    time.sleep(0.1)
