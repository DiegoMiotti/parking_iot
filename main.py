import machine
import time
import network
from machine import Pin, PWM
from hcsr04 import HCSR04
from umqtt.simple import MQTTClient


# Configuración de red WiFi y MQTT
ssid = 'Wokwi-GUEST'
wifipassword = ''
mqtt_server = 'io.adafruit.com'
port = 1883
user = 'DiegoMiotti'
password = 'pass'
client_id = 'Estacionamiento_IOT'
topic_barrera = 'DiegoMiotti/feeds/controlbarreras'
topic_capacidad = 'DiegoMiotti/feeds/capacidadestacionamiento'

# Conexión WiFi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, wifipassword)
while not sta_if.isconnected():
    print("Conectando a WiFi...")
    time.sleep(0.5)
print("Conectado a WiFi!")
print(sta_if.ifconfig())

# Conexión al broker MQTT
def mqtt_callback(topic, msg):
    global barrera_controlada
    mensaje = msg.decode('utf-8')
    #print(f"Mensaje recibido: {mensaje}")
    if mensaje == "ON":
        barrera_controlada = True
        print("\n////Barreras activadas. Los autos pueden ingresar. Estacionamiento Abierto. ////\n")
    elif mensaje == "OFF":
        barrera_controlada = False
        print("\n****Barreras desactivadas. No se permite ingreso, solo egreso de autos. Estacionamiento Cerrado. ****\n")


###------------------------------------Declaracion de variables------------------------------------###

# inicializacion sensores, servo y leds
sensorBarreraEntrada = HCSR04(trigger_pin=1, echo_pin=0)
sensorBarreraSalida = HCSR04(trigger_pin=5, echo_pin=4)
pwmServoEntrada = PWM(Pin(2, Pin.OUT))
pwmServoEntrada.freq(50)
pwmServoSalida = PWM(Pin(8, Pin.OUT))
pwmServoSalida.freq(50)
led_rojo = Pin(7, Pin.OUT)
led_verde = Pin(6, Pin.OUT)

# setear los servos en la posicion cerrada 
pwmServoEntrada.duty(75)
pwmServoSalida.duty(75)

# variables
max_autos = 10
autos_actuales = 0
barrera_controlada = True #por seguridad q inicie con las barreras cerradas. 



# Banderas
bandAutoEntradaDetectado = 0
bandAutoSalidaDetectado = 0
banderaMensaje = 0

# estados iniciales de las maqs de estado
ESPERA = 0
ACTIVO = 1

# default inicio 
estadoEntrada = ESPERA
estadoSalida = ESPERA


##3----------------------------------------Desarrollo de funciones---------------------------###

# funcion conexion al mqtt 
def conectar_mqtt():
    conexionMQTT = MQTTClient(client_id, mqtt_server, user=user, password=password, port=port)
    conexionMQTT.set_callback(mqtt_callback)
    conexionMQTT.connect()
    conexionMQTT.subscribe(topic_barrera)
    print("Conectado a MQTT y suscrito a:", topic_barrera , "\ny enviara la capacidad a: ", topic_capacidad)
    return conexionMQTT
cliente_mqtt = conectar_mqtt()



# funcion para enviar la cant de autos al adafruit 
def enviarCapacidad(cliente, autos_actuales):
    mensaje = str(autos_actuales)
    cliente.publish(topic_capacidad, mensaje)
    #print(f"Publicado en el dashboard: {mensaje} autos actuales")



# funcion para manejar los leds 
def actualizar_leds():
    if not barrera_controlada:      #se prende cuando esta desactivado desde adafr
        led_rojo(1)
        led_verde(0)
    else:
        if autos_actuales >= max_autos:
            led_rojo.value(1)
            led_verde.value(0)
        else:
            led_rojo.value(0)
            led_verde.value(1)




# funcion para controlar el servo
def abrirBarrera(servo):
    servo.duty(125)

def cerrarBarrera(servo):
    servo.duty(75)



#-------------------------------------Desarrollo de las Maquinas de estados ------------------------------####

# Maq de estado entrada
def maquinaEstadoEntrada():
    global estadoEntrada, autos_actuales, bandAutoEntradaDetectado,banderaMensaje
    distanciaEntrada = sensorBarreraEntrada.distance_cm()
    
    # Estado ESPERA = 0
    if estadoEntrada == ESPERA:
        if barrera_controlada and distanciaEntrada < 100 and bandAutoEntradaDetectado == 0 and autos_actuales < max_autos:
            print("Auto detectado en entrada, abriendo barrera...")
            abrirBarrera(pwmServoEntrada)
            bandAutoEntradaDetectado = 1
            banderaMensaje = 0
            
            estadoEntrada = ACTIVO

        if autos_actuales==max_autos and banderaMensaje == 0:
            print("Estacionamiento lleno.")
            banderaMensaje = 1


    # Estado ACTIVO = 1 
    if estadoEntrada == ACTIVO:
        if distanciaEntrada > 250 and bandAutoEntradaDetectado == 1:
            print("Auto ingreso, cerrando barrera...")
            cerrarBarrera(pwmServoEntrada)
            bandAutoEntradaDetectado = 0
            autos_actuales += 1
            print("Hay ",autos_actuales, " autos en el Estacionamiento. ")
            enviarCapacidad(cliente_mqtt, autos_actuales)
            
            estadoEntrada = ESPERA



#--------------------------------------------------------------------------------####
#Maq estado salida
def maquinaEstadoSalida():
    global estadoSalida, autos_actuales, bandAutoSalidaDetectado
    distanciaSalida = sensorBarreraSalida.distance_cm()

    # Estado ESPERA = 0
    if estadoSalida == ESPERA:  #no pregunta x la barrera_controlada para que los autos salgan cuando esta cerrado el parking 
        if distanciaSalida < 100 and bandAutoSalidaDetectado == 0 and autos_actuales > 0:
            print("Auto detectado en salida, abriendo barrera...")
            abrirBarrera(pwmServoSalida)
            bandAutoSalidaDetectado = 1
            
            estadoSalida = ACTIVO


    # Estado ACTIVO =1 
    if estadoSalida == ACTIVO:
        if distanciaSalida > 250 and bandAutoSalidaDetectado == 1:
            print("Auto salio, cerrando barrera...")
            cerrarBarrera(pwmServoSalida)
            bandAutoSalidaDetectado = 0
            autos_actuales -= 1
            print("Hay ",autos_actuales, " autos en el Estacionamiento. ")
            enviarCapacidad(cliente_mqtt, autos_actuales)
            
            estadoSalida = ESPERA




while True:
    try:

        #llamadp a funciones
        cliente_mqtt.check_msg()
        maquinaEstadoEntrada()
        maquinaEstadoSalida()
        actualizar_leds()
        time.sleep(0.5)

    except OSError as e:
        print("Error: ", e)
        time.sleep(5)
        machine.reset()