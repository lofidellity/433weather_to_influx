# Thanks for the code to start Mike
#!/bin/python3.4
import json, os

from influxdb import InfluxDBClient
from subprocess import Popen, PIPE

client = InfluxDBClient(host=os.environ['influxdb_host'], port=os.environ['influxdb_port'], database='weather')
client.create_database('weather')
with Popen(['/usr/local/bin/rtl_433', '-F', 'json', '-C', 'customary'], stdout=PIPE, bufsize=1, universal_newlines=True) as data:
    for line in data.stdout:
        try:
            tjson = json.loads(line)
        except ValueError:
            print("Error parsing data from: " + line)
        else:
            if 'id' in tjson or 'sensor_id' in tjson:
                odd_data = True
                temperature_F = wind_speed_mph = humidity = None
                json_body = []
                id = tjson['id'] if 'id' in tjson else tjson['sensor_id']
                if 'temperature_F' in tjson:
                    temp = "{:03.1f}".format(tjson['temperature_F'])
                    json_body.append({'measurement': 'temperature', 'tags': {'id': id }, 'fields': { 'value': float(temp) } })
                    odd_data = False
                if 'wind_speed_mph' in tjson:
                    wind_speed = tjson['wind_speed_mph']
                    json_body.append({'measurement': 'wind_speed', 'tags': {'id': id }, 'fields': { 'value': wind_speed } })
                    odd_data = False
                if 'wind_avg_mi_h' in tjson:
                    wind_speed = tjson['wind_avg_mi_h']
                    json_body.append({'measurement': 'wind_speed', 'tags': {'id': id }, 'fields': { 'value': wind_speed } })
                    odd_data = False
                if 'humidity' in tjson:
                    humidity = tjson['humidity']
                    json_body.append({'measurement': 'humidity', 'tags': {'id': id }, 'fields': { 'value': humidity} })
                    odd_data = False

                expected_keys = {'humidity', 'wind_avg_mi_h', 'wind_speed_mph', 'temperature_F', 'time', 'model', 'id', 'channel', 'battery_ok', 'mic'}
                if set(tjson.keys()) >= expected_keys:
                    print("RAW DATA: " + line) 
                    print("New data " + str(json_body))
                    print("Unexpected keys are: " + str(set(tjson.keys()).difference(expected_keys)))
                    print("\n\n\n")
                client.write_points(json_body)
