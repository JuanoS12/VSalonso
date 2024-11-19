import random
import math

class Neurona:
    def __init__(self, entradas, beta1=0.9, beta2=0.999, epsilon=1e-8, tasa_aprendizaje=0.95):
        self.pesos = [random.uniform(-1, 1) for _ in range(entradas)]
        self.bias = random.uniform(-1, 1)
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.tasa_aprendizaje = tasa_aprendizaje
        self.m_pesos = [0] * len(self.pesos)
        self.v_pesos = [0] * len(self.pesos)
        self.m_bias = 0
        self.v_bias = 0
        self.t = 0

    def activar(self, entradas):
        suma = sum(peso * entrada for peso, entrada in zip(self.pesos, entradas)) + self.bias
        return 1 / (1 + math.exp(-suma))  # Función sigmoide

    def entrenar(self, entradas, salida_deseada):
        self.t += 1
        salida_obtenida = self.activar(entradas)
        error = salida_deseada - salida_obtenida
        
        derivada = salida_obtenida * (1 - salida_obtenida)
        grad_pesos = [error * derivada * entrada for entrada in entradas]
        grad_bias = error * derivada

        # Adam optimizer
        self.m_pesos = [self.beta1 * m + (1 - self.beta1) * g for m, g in zip(self.m_pesos, grad_pesos)]
        self.v_pesos = [self.beta2 * v + (1 - self.beta2) * (g ** 2) for v, g in zip(self.v_pesos, grad_pesos)]
        self.m_bias = self.beta1 * self.m_bias + (1 - self.beta1) * grad_bias
        self.v_bias = self.beta2 * self.v_bias + (1 - self.beta2) * (grad_bias ** 2)

        # Corrección de sesgos
        m_pesos_corr = [m / (1 - self.beta1 ** self.t) for m in self.m_pesos]
        v_pesos_corr = [v / (1 - self.beta2 ** self.t) for v in self.v_pesos]
        m_bias_corr = self.m_bias / (1 - self.beta1 ** self.t)
        v_bias_corr = self.v_bias / (1 - self.beta2 ** self.t)

        # Actualización de pesos y bias
        self.pesos = [peso - self.tasa_aprendizaje * m / (math.sqrt(v) + self.epsilon)
                      for peso, m, v in zip(self.pesos, m_pesos_corr, v_pesos_corr)]
        self.bias -= self.tasa_aprendizaje * m_bias_corr / (math.sqrt(v_bias_corr) + self.epsilon)


class RedNeuronal:
    def __init__(self, entradas, neuronas_ocultas, salidas):
        self.neuronas = [Neurona(entradas) for _ in range(neuronas_ocultas)]
        self.salidas = [Neurona(neuronas_ocultas) for _ in range(salidas)]

    def entrenar(self, entradas, salidas, epochs=1000):
        for epoch in range(epochs):
            for entrada, salida_deseada in zip(entradas, salidas):
                ocultas = [neurona.activar(entrada) for neurona in self.neuronas]
                salida = [neurona.activar(ocultas) for neurona in self.salidas]
                
                # Entrenamiento de la capa de salida
                for i, neurona in enumerate(self.salidas):
                    neurona.entrenar(ocultas, salida_deseada[i])
                
                # Retropropagación para neuronas ocultas
                for neurona in self.neuronas:
                    error_oculto = sum(salida[i] * (salida_deseada[i] - salida[i]) for i in range(len(salida)))
                    neurona.entrenar(entrada, error_oculto)


