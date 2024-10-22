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

broker = "192.168.192.150"

var_standard = {'data':'insert_data_object','name':'insert_var_name'}
cmd_standard = {}

topic_var = "everest/evse_manager/evse/var"
topic_cmd = "everest/evse_manager/evse/cmd"


async def publish_var_json(client, var=0):
    while True:
        for var in vars_dict_key_list:
            await asyncio.sleep(0.2)
            var_standard['data'], var_standard['name'] = vars_dict[var], var
            msg = json.dumps(var_standard, separators=(",",":"))
            await client.publish(topic_var, payload=msg)


async def read_cmd_to_dict(client):
    await client.subscribe(topic_cmd)
    async for message in client.messages:
        print(json.loads(message.payload))


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