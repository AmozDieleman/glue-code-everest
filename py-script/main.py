### Python 3.12.6

import json
import sys
import time

from threading import Thread
from paho.mqtt import client as mqtt_client

vars_dict = {
    "evse_id": "NL*DCO*E1234*1",
    "ready": False,  # Placeholder for boolean; update as needed
    "session_event": {
        "uuid": "sessionString",
        "timestamp": "date-time",
        "event": "eventEnum"
    },
    "limits": {
        "uuid": "EVSE",
        "max_current": 32,
        "nr_of_phases_available": 1
    },
    "enforced_limits": {
        "uuid": "NODE",
        "valid_until": "date-time",
        "limits_root": {
            "total_power_W": 20000
        }
    },
    "hw_capabilities": {
        "max_current_A_import": 0.0,  # Placeholder for float; update as needed
        "min_current_A_import": 0.0,  # Placeholder for float; update as needed
        "max_phase_count_import": 1,
        "min_phase_count_import": 1,
        "max_current_A_export": 0.0,  # Placeholder for float; update as needed
        "min_current_A_export": 0.0,  # Placeholder for float; update as needed
        "max_phase_count_export": 1,
        "min_phase_count_export": 1,
        "supports_changing_phases_during_charging": False,
        "connector_type": "IEC62196Type2Cable"
    },
    "ev_info": {  # Optional field, include only if available
        "soc": "%",
        "present_voltage": "V",
        "present_current": "A",
        "target_voltage": "V",
        "target_current": "A",
        "maximum_current_limit": "A",
        "minimum_current_limit": "A",
        "maximum_voltage_limit": "V",
        "minimum_voltage_limit": "V",
        "estimated_time_full": "date-time",
        "departure_time": "date-time",
        "estimated_time_bulk": "date-time",
        "evcc_id": "MAC-address",
        "remaining_energy_needed": "Wh",
        "battery_capacity": "Wh",
        "battery_full_soc": "%",
        "battery_bulk_soc": 80
    },
    "telemetry": {
        "evse_temperature_C": 0.0,  # Placeholder for float; update as needed
        "fan_rpm": 0,
        "supply_voltage_12v": 0.0,  # Placeholder for float; update as needed
        "supply_voltage_minus_12v": 0.0,  # Placeholder for float; update as needed
        "relais_on": False  # Placeholder for boolean; update as needed
    },
    "powermeter": {
        "timestamp": "date-time",
        "meter_id": "sketchy_multiplication",
        "energy_Wh_import": {
            "total": 0.0  # Placeholder for float; update as needed
        },
        "energy_Wh_export": {  # Optional field, include only if available
            "total": 0.0  # Placeholder for float; update as needed
        },
        "current_A": 0.0,  # Placeholder for float; update as needed, optional
        "voltage_V": 0.0,  # Placeholder for float; update as needed, optional
        "power_W": 0.0     # Placeholder for float; update as needed, optional
    }
}

vars_dict_key_list = list(vars_dict.keys())


var_standard = {'data':'insert_data_object','name':'insert_var_name'}
cmd_standard = {}

broker ="192.168.192.150"
port = 1883
topic_var = "everest/evse_manager/evse/var"
topic_cmd = "everest/evse_manager_1/evse/cmd"
client_id = "dco-evse-1234-1"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Succesfully connected to MQTT broker")
        else:
            print("Failed to connect, return code %d/n", rc)
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(broker,port)
    return client


def publish_var_json(client):
    var = 0
    while True:
        time.sleep(0.2)
        var_standard['data'], var_standard['name'] = vars_dict[vars_dict_key_list[var%9]], vars_dict_key_list[var%9]
        msg = json.dumps(var_standard, separators=(",",":"))
        result = client.publish(topic_var, msg)
        # result: [0, 1]
        # status = result[0]
        # if status == 0:
        #     print(f"Succesfully sent var")
        # else:
        #     print(f"Failed to send var")
        var += 1

def read_cmd_to_dict(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{json.loads(msg.payload.decode())}")

    client.subscribe(topic_cmd)
    client.on_message = on_message




def run():
    try:
        client = connect_mqtt()
        t1 = Thread(target=read_cmd_to_dict, args=(client,))
        t2 = Thread(target=publish_var_json, args=(client,))
        # read_cmd_to_dict(client)
        # publish_var_json(client)
        t1.start()
        t2.start()
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop()
        t1.join()
        t2.join()
        sys.exit(0)

if __name__ == '__main__':
    run()