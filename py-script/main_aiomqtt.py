import asyncio
import aiomqtt
import json


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
        "soc": 0,
        "present_voltage": 0.0,
        "present_current": 0.0,
        "target_voltage": 0.0,
        "target_current": 0.0,
        "maximum_current_limit": 0.0,
        "minimum_current_limit": 0.0,
        "maximum_voltage_limit": 0.0,
        "minimum_voltage_limit": 0.0,
        "estimated_time_full": "date-time",
        "departure_time": "date-time",
        "estimated_time_bulk": "date-time",
        "evcc_id": "MAC-address",
        "remaining_energy_needed": 0.0,
        "battery_capacity": 0.0,
        "battery_full_soc": 100,
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

cmds_dict = {
    "get_evse":{
        "args":{},
        "result":{
            "id":1,
            "connectors":[[1,"cCCS2"]]
        }
    },

    # Add function to check status EVSE after command, result is true when turned on after cmd and false if turned off after cmd. 
    "enable_disable":{
        "args":{
            "connector_id":"",
            "cmd_source":"insert source"
        },
        "result":True
    },

    "authorize_response":{
        "args":{
            "provided_token":"insert token",
            "validation_result":"insert result"
        },
        "result":{}
    },
    
    # No args or result, cannot start transaction after call.
    "withdraw_authorization":{
        "args":{},
        "to_do":"don't start transaction",
        "result":{}
    },

    # Call to signal that EVSE is reserved, return True if reservation is accepted, false if rejected.
    "reserve":{
        "args":{
            "reservation_id":""
        },
        "result":False
    },

    # No args or result, EVSE no longer reserved after call.
    "cancel_reservation":{
        "args":{},
        "to_do":"cancel_reservation()",
        "result":{}
    },

    # No args or result, set EVSE to faulted externally after call.
    "set_faulted":{
        "args":{},
        "to_do":"set_evse_faulted()",
        "result":{}
    },

    # No args, pause charging, return True if charging paused after call, False otherwise.
    "pause_charging":{
        "args":{},
        "result":False
    },

    # No args, resume charging, return True if charging resumed after call, False otherwise.
    "resume_charging":{
        "args":{},
        "result": False
    },

    # Forces connector to unlock immediately, return True if succesfully unlocked, False otherwise.
    "force_unlock":{
        "args":{
            "connector_id":0
        },
        "result":False
    },

    # No result, set energy limits at specified node
    "set_external_limits":{
        "args":{},
        "result":{}
    },

    # No args, return True if call was used by EVSE
    "external_ready_to_start_charging":{
        "args":{},
        "result":False
    }
}

# To be implemented in cmds_dict
    # Request to stop transaction, return True if succesful.
    # "stop_transaction":{
    #     "request"{

    #     },
    #     "result":False
    # },
    # No result, set Contract Certificate
    # "set_get_certificate_response":{
    #     "certificate_response":{

    #     }
    # },

cmds_dict_key_list = list(cmds_dict.keys())


broker = "192.168.192.150"

var_standard = {"data":"insert_data_object","name":"insert_var_name"}
cmd_standard = {"data":{"id":"call_id","origin":"evse_manager","retval":{}},"name":"call_name","type":"result"}

topic_var = "everest/evse_manager/evse/var"
topic_cmd = "everest/evse_manager/evse/cmd"


def cmd_handler(cmd):
    cmds_dict[cmd["name"]]["args"]  = cmd["data"]["args"]
    cmd_standard["data"]["id"]      = cmd["data"]["id"]
    cmd_standard["data"]["retval"]  = cmds_dict[cmd["name"]]["result"]
    cmd_standard["name"]            = cmd["name"]
    
    msg = json.dumps(cmd_standard, separators=(",",":"))
    
    return msg


async def publish_var_json(client, var=0):
    while True:
        for var in vars_dict_key_list:
            await asyncio.sleep(0.2)
            var_standard["data"], var_standard["name"] = vars_dict[var], var
            msg = json.dumps(var_standard, separators=(",",":"))
            await client.publish(topic_var, payload=msg)


async def read_cmd_to_dict(client):
    await client.subscribe(topic_cmd)
    async for message in client.messages:
        print(json.loads(message.payload))
        if message.payload["type"] == "call":
            msg = cmd_handler(json.loads(message.payload))
            await client.publish(topic_cmd, payload=json.dumps(msg))


async def main():
    async with aiomqtt.Client(broker) as client:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(read_cmd_to_dict(client))
            tg.create_task(publish_var_json(client))


def run():
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to run: {e}")


run()

# if __name__ == "__main__":
#     run()

# print(cmd_standard["data"]["id"])

# cmd = json.loads('{"data":{"args":"","id":"123412341234","origin":"auth"},"name":"get_evse","type":"call"}')
# print(cmd["data"]["id"])
# msg = cmd_handler(cmd)
# print(msg)