import json
import time

from paho.mqtt import client as mqtt_client



broker ="localhost"
port = 1883
topic = "everest/evse_manager/evse/"
client_id = f'dco-evse-1234-1'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Succesfully connected to MQTT broker")
        else:
            print("Failed to connect, return coge %d/n", rc)
    
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(broker,port)
    return client


def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()

if __name__ == '__main__':
    run()