def normalizar_datos(datos):
    max_valor = 32768.0  # Valor máximo del sensor (para acelerómetro y giroscopio de 16 bits)
    return [dato / max_valor for dato in datos]
