
import googlemaps
import yaml
import csv
import sqlite3
import os

import datetime

api_key = os.getenv("API_KEY")
gmaps = googlemaps.Client(key=api_key)

with open('config.yaml') as f:
	inputs=yaml.load(f.read())

commute_times={}

time = datetime.datetime.now()
if time.hour < 12:
	t=gmaps.distance_matrix(origins=inputs['homes'], destinations=inputs['destinations'], departure_time=time)
else:
	t=gmaps.distance_matrix(origins=inputs['destinations'], destinations=inputs['homes'], departure_time=time)

l=[]

for i_o, origin in enumerate(t['origin_addresses']):
	for i_d, destination in enumerate(t['destination_addresses']):
		duration = t['rows'][i_o]['elements'][i_d]['duration_in_traffic']['value']
		row ={
			'origin':origin,
			'destination':destination,
			'departure':"{time:%Y-%m-%d %H:%M}".format(time=time),
			'duration':duration
		}
		l.append(row)

conn=sqlite3.connect('db/commute.sqlite')
c=conn.cursor()
#c.execute('CREATE TABLE IF NOT EXISTS "commute" (`origin`TEXT,`destination`TEXT,`departure`TEXT,`duration`TEXT)')
c.executemany('INSERT INTO commute VALUES (?,?,?,?)', [(d['origin'], d['destination'], d['departure'], d['duration']) for d in l])
conn.commit()
conn.close()
