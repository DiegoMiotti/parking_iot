# Parking IoT System  

Un sistema de estacionamiento inteligente basado en IoT. Este proyecto fue realizado para la materia de Fundamentos de los sistemas embebidos de la UNLAM. Se utiliza sensores ultrasónicos, un módulo MQTT, y microcontroladores para gestionar automáticamente el acceso y la capacidad de un estacionamiento.  

Proyecto en wokwi
link: https://wokwi.com/projects/417687038690120705

## 🚗 **Características**  
- Detección automática de vehículos en las barreras de entrada y salida.  
- Gestión remota de barreras a través de Adafruit IO.  
- Indicadores LED para mostrar el estado del estacionamiento (capacidad y acceso).  
- Máquinas de estado que controlan las barreras de forma segura.  
- Envío en tiempo real de la capacidad del estacionamiento al dashboard MQTT.  

## 📋 **Requisitos previos**  
- Un microcontrolador compatible con MicroPython (como ESP32 o ESP8266).  
- Sensores ultrasónicos (HC-SR04) para detectar vehículos.  
- Servos para las barreras de entrada y salida.  
- LEDs para indicadores visuales.  
- Cuenta en [Adafruit IO](https://io.adafruit.com/) para gestionar el sistema MQTT.  

## ⚙️ **Configuración del proyecto**  

1. **Conexión WiFi**:  
   Asegúrate de configurar tu red WiFi en el código:  
   ```python
   ssid = 'Tu_SSID'
   wifipassword = 'Tu_Contraseña'


🛠️ Cómo ejecutar el sistema
Sube el archivo al microcontrolador utilizando Thonny u otro editor compatible con MicroPython.
Enciende el dispositivo y verifica que se conecta correctamente a WiFi y al broker MQTT.
Accede al dashboard de Adafruit IO para controlar las barreras y monitorear la capacidad en tiempo real.
