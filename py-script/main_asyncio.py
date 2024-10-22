### Python 3.12.6

import json
import sys
import time
import asyncio

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
topic_cmd = "everest/evse_manager/evse/cmd"
client_id = "dco-evse-1234"
# client_id_publish = "dco-pub-1234"
# client_id_read = "dco-rd-1234"

def connect_mqtt():
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.connect(broker,port)
    return client


async def publish_var_json(client: mqtt_client, var=0):
    var_standard['data'], var_standard['name'] = vars_dict[var], var
    msg = json.dumps(var_standard, separators=(",",":"))
    client.publish(topic_var, msg)


async def read_cmd_to_dict(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f'Received {json.loads(msg.payload.decode())}')

    client.subscribe(topic_cmd)
    client.on_message = on_message


async def main():

    try:
        client = connect_mqtt()
    except Exception as e:
        print(f'Failed to connect: {e}')
        exit(-1)

    print()

    tasks: set[asyncio.Task[None]] = set()

    

    task_publish_var_json = asyncio.create_task(publish_var_json(client))
    task_read_cmd_to_dict = asyncio.create_task(read_cmd_to_dict(client))
    client.loop_forever()

    print()

    tasks.add(task_publish_var_json)
    tasks.add(task_read_cmd_to_dict)

    try:
        exceptions = asyncio.gather(*tasks, return_exceptions=False)
        await exceptions

    except Exception as e:
        print(f'Exited main: {e}')

    exit(0)


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Terminated manually')
        exit(0)

if __name__ == '__main__':
    run()