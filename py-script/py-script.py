from paho.mqtt import client as mqtt_client

broker ="localhost"
port = 1883
topic = "everest/evse_manager/evse/"
client_id = f'dco-pyscript-1901'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        
