# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, url_for, make_response, abort
import json
from uuid import uuid4

app_url = '/pijaginw/findyourway'
app = Flask(__name__)
app.secret_key = '8@*73fdr_1$*rtrp3*(()12a##'

#from werkzeug.debug import DebuggedApplication
#app.debug = True
#app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

cities = [
	{'id':0, 'name':'Suwalki', 'short':'SUW', 'connections':[
		{'dest':'WAW', 'dist':300},
		{'dest':'PZN', 'dist':550},
		{'dest':'SDL', 'dist':270},
		{'dest':'GDA', 'dist':340}
	]},
	{'id':1, 'name':'Warszawa', 'short':'WAW', 'connections':[
		{'dest':'SUW', 'dist':300},
		{'dest':'KRK', 'dist':300},
		{'dest':'PZN', 'dist':310},
		{'dest':'SDL', 'dist':90},
		{'dest':'GDA', 'dist':420},
		{'dest':'LDZ', 'dist':130},
		{'dest':'LUB', 'dist':170},
		{'dest':'WRO', 'dist':360}
	]},
	{'id':2, 'name':'Krakow', 'short':'KRK', 'connections':[
		{'dest':'WAW', 'dist':300},
		{'dest':'PZN', 'dist':450},
		{'dest':'SDL', 'dist':370},
		{'dest':'WRO', 'dist':270}
	]},
	{'id':3, 'name':'Siedlce', 'short':'SDL', 'connections':[
		{'dest':'WAW', 'dist':90},
		{'dest':'KRK', 'dist':370},
		{'dest':'SUW', 'dist':270},
		{'dest':'LUB', 'dist':140}
	]},
	{'id':4, 'name':'Poznan', 'short':'PZN', 'connections':[
		{'dest':'WAW', 'dist':310},
		{'dest':'KRK', 'dist':450},
		{'dest':'SUW', 'dist':550},
		{'dest':'WRO', 'dist':170},
		{'dest':'SZC', 'dist':260},
		{'dest':'LDZ', 'dist':220}
	]},
	{'id':5, 'name':'Gdynia', 'short':'GDY', 'connections':[
		{'dest':'GDA', 'dist':22},
		{'dest':'SZC', 'dist':340}
	]},
	{'id':6, 'name':'Gdansk', 'short':'GDA', 'connections':[
		{'dest':'GDY', 'dist':22},
		{'dest':'SZC', 'dist':360},
		{'dest':'WAW', 'dist':420},
		{'dest':'SUW', 'dist':340}
	]},
	{'id':7, 'name':'Lublin', 'short':'LUB', 'connections':[
		{'dest':'SDL', 'dist':140},
		{'dest':'KRK', 'dist':320},
		{'dest':'WAW', 'dist':170}
	]},
	{'id':8, 'name':'Szczecin', 'short':'SZC', 'connections':[
		{'dest':'PZN', 'dist':260},
		{'dest':'WRO', 'dist':370},
		{'dest':'GDA', 'dist':360},
		{'dest':'GDY', 'dist':340}
	]},
	{'id':9, 'name':'Lodz', 'short':'LDZ', 'connections':[
		{'dest':'WAW', 'dist':130},
		{'dest':'PZN', 'dist':220}
	]},
	{'id':10, 'name':'Wroclaw', 'short':'WRO', 'connections':[
		{'dest':'WAW', 'dist':360},
		{'dest':'PZN', 'dist':170},
		{'dest':'SZC', 'dist':370},
		{'dest':'KRK', 'dist':270}
	]}
]

routes = []

### -----------------------------------------------------MIASTA-------------------------------------------------

### wyswietlenie wszystkich miast
@app.route(app_url + '/cities', methods=['GET'])
def get_cities():

	response = make_response( json.dumps(cities), 200, {'content-type': 'application/json'} )
	return response

### wyswietlenie konkretnego miasta
@app.route('/pijaginw/findyourway/city' + '/<int:city_id>', methods=['GET'])
def show_city(city_id):

	for city in cities:
		if city["id"] == city_id:
			response = make_response( json.dumps(city), 200, {'content-type': 'application/json'} )
			return response

	return '\nNie znaleziono miasta o podanym numerze ID.\n', 404

### zwraca baze miast w formacie JSON, ale tylko jako (id - nazwa - skrot)
@app.route(app_url + '/compressed_cities', methods=['GET'])
def get_compressed_cities():

	data = []
	for city in cities:
		new_city = {}
		new_city['id'] = city['id']
		new_city['name'] = city['name']
		new_city['short'] = city['short']
		data.append(city)

	if data != None:
		response = make_response( json.dumps(data), 200, {'Content-Type': 'application/json'})
		return response
	else:
		return '\nSomething went wrong. Could not get the cities.\nError: ' + str(e), 500


### zwroci nastepujacy JSON:
###
### {'id':liczba, 'name':'', 'short':'', 'connections': []}
###
@app.route(app_url + '/city', methods=['POST'])
def add_city():

	d = request.get_data()
	try:
		data = json.loads(d)

		if (data['name'] == '') or (data['short'] == '') or (data['connections'] == ''):
			#response = make_response( 'Brak danych do utworzenia nowego miasta.\n', 304, {'Content-Type': 'text/html'} )
			return 'Brak danych do utworzenia nowego miasta.\n', 304

		new_city = { 
			"id": len(cities), 
			"name": data["name"], 
			"short": data["short"] 
		}
		new_city["connections"] = []

		try:
			connections = json.loads(data["connections"])
			for con in connections:
				new_connection = {"dest": con["dest"], "dist": con["dist"]}
				new_city["connections"].append(new_connection)

				for c in cities:
					if c["short"] == con["dest"]:
						nc = {"dest": new_city["short"], "dist": con["dist"]}
						c["connections"].append(nc)

			cities.append(new_city)

			response = make_response( json.dumps(new_city), 200, {'Content-Type': 'application/json',
																	'Location': "http://edi.iem.pw.edu.pl/pijaginw/findyourwayapp/city/" 
																				+ str(new_city["id"])} )
			return response

		except ValueError, e:
			return 'Polaczenia musza byc podane w formacie JSON\nconnections= %s\n' % str(data["connections"]), 400

	except ValueError, e:
		return 'Oczekuje formatu JSON\nrequest.data= %s\n' % d, 400

### umozliwa edycje pelnej nazwy miasta oraz dodawanie polaczen z istniejacymi miastami
@app.route('/pijaginw/findyourway/city' + '/<int:city_id>', methods=['POST'])
def edit_city(city_id):

	data = request.get_data()
	try:
		arguments = json.loads(data)

		if ('newName' not in arguments) and ('newConnections' not in arguments):
			response = make_response( 'Nie podano danych do edycji.', 304, {'content-type': 'text/html'} )
			return response

		for city in cities:
			if city['id'] == city_id:
				if 'newName' in arguments:

					city["name"] = arguments.get('newName')
					response = make_response( json.dumps(city), 200, {'content-type': 'application/json'} )
					return response

				if 'newConnections' in arguments:	
																### ponizej aktualizacja polaczen dla bazy miast

					try:
						connections = json.loads(arguments.get('newConnections'))

						new_connections = {}
						for con in connections:
							city["connections"].append({"dest": con["dest"], "dist": con["dist"]})
							new_connections = {"dest": city["short"], "dist": con["dist"]}

							for c in cities:
								if c["short"] == con["dest"]:
									c["connections"].append(new_connections)


						response = make_response( json.dumps(city), 200, {'content-type': 'application/json'} )
						return response

					except ValueError, e:
						return 'Polaczenia musza byc podane w formacie JSON\nconnections= %s\n' % city["connections"], 400


		return '\nNie znaleziono miasta o podanym numerze ID.\n', 404

	except ValueError, e:
		return 'Oczekuje formatu JSON\nrequest.data= %s\n' % request.get_data(), 400


@app.route('/pijaginw/findyourway/city' + '/<int:city_id>', methods=['DELETE'])
def remove_city(city_id):

	for city in cities:
		if city['id'] == city_id:
			for con in city['connections']:
				for c in cities:
					if c['short'] == con['dest']:
						for connection in c['connections']:
							if connection['dest'] == city['short']:
								c['connections'].remove(connection)

			cities.remove(city)

			return '\nMiasto zostalo usuniete.\n', 410

	return 'Nie znaleziono miasta o podanym numerze ID.\n', 404


### ----------------------------------------------------TRASY-----------------------------------------------

### zwroci nastepujacy JSON:
###
### {'from':'', 'to':'', 'route':liczba, 'id':liczba, 'through': lista}
###
@app.route(app_url + '/routes', methods=['POST'])
def find_route():

	if request.method == 'POST':

		data = request.get_data()
		try:
			arguments = json.loads(data)
			if (arguments.get('from') is None) or (arguments.get('to') is None):
				return 'Brak danych - miasta poczatkowego i docelowego.\n', 400

			city_from = arguments.get('from')
			city_to = arguments.get('to')

			for c in cities:
				if (c['short'] == str(city_from)) or (c['name'] == str(city_from)):
					city_from = cities.index(c)
				if (c['short'] == str(city_to)) or (c['name'] == str(city_to)):
					city_to = cities.index(c)
			
			### jesli dane sa w postaci innej niz numery id --> zamieniam na numery id
			'''if (len(city_from)) == 3 and (len(city_to) == 3): ### na podstawie skrotu
				city_from = get_city_id(cities,city_from)
				city_to = get_city_id(cities,city_to)

			elif (len(city_from)) > 3 and (len(city_to) > 3): ### na podstawie nazwy
				city_from = get_city_id_by_name(cities,city_from)
				city_to = get_city_id_by_name(cities,city_to)
			'''
			newRoute = dijkstra(cities, len(cities), city_from, city_to)

			if newRoute == None:
				return 'Trasa nie zostala odnaleziona.', 500

			### nowa trasa jest zawsze w formacie {id, pelne nazwy miast, dlugosc trasy}, wiec teraz zamieniam id na nazwy
			new_route = {
				"id": str(uuid4()),
				"from": get_name_by_id(cities,city_from),
				"to": get_name_by_id(cities,city_to),
				"route": newRoute['distance'],
				"through": newRoute['through']
			}
			
			global routes
			routes.append(new_route)

			response = make_response(json.dumps(new_route), 200, {'content-type': 'application/json', 
																	'Location': app_url + '/routes/' + new_route["id"]})
			return response

		except ValueError, e:
			return 'Usluga oczekuje formatu JSON\nrequest.data= %s\n' % request.get_data(), 400


@app.route( app_url + '/routes' + '/<route_id>', methods=['GET'])
def show_route(route_id):
	
	global routes
	for route in routes:
		if route["id"] == route_id:
			return json.dumps(route)
	return '\nNie znaleziono trasy o podanym numerze ID.\n', 404


### -----------------------------------------POLACZENIA MIEDZY MIASTAMI--------------------------------------


@app.route( app_url + '/connections', methods=['GET'])
def connection_editor():

	response = make_response( json.dumps(cities), 200, {'content-type':'application/json'})
	return response

### w odpowiedzi wysyla JSON z miastem "city_from", dla ktorego zostalo edytowane polaczenie
### (oczywiscie polaczenie dla drugiego miasta rowniez jest edytowane)
@app.route( app_url + '/connections' + '/<city_from>' + '/<city_to>', methods=['PUT'])
def edit_connection(city_from, city_to):

	data = request.get_data()
	try:
		arguments = json.loads(data)
		if arguments.get('newValue') is None:
			response = make_response( 'Bledne dane.', 400, {'content-type':'text/html'})
			return response

		new_value = arguments.get('newValue')
		for cityFrom in cities:
			if cityFrom["short"] == str(city_from):
				for c in cityFrom["connections"]:
					if c["dest"] == str(city_to):
						c["dist"] = int(new_value)
						for cityTo in cities:
							if cityTo["short"] == str(city_to):
								for c2 in cityTo["connections"]:
									if c2["dest"] == str(city_from):
										c2["dist"] = int(new_value)

										response = make_response( json.dumps(cityFrom), 200, {'content-type':'application/json'})
										return response

		return 'Nie znaleziono polaczenia pomiedzy podanymi miastami.\nZ: %s, DO: %s\n' % (city_from, city_to), 404

	except ValueError, e:
		return 'Usluga oczekuje formatu JSON\nrequest.data= %s\n' % request.get_data(), 400

@app.route( app_url + '/connections' + '/<city_from>' + '/<city_to>', methods=['DELETE'])
def delete_connection(city_from, city_to):

	for cityFrom in cities:
		if cityFrom["short"] == str(city_from):
			for c in cityFrom['connections']:
				if c["dest"] == str(city_to):
					cityFrom['connections'].remove(c)
					for cityTo in cities:
						if cityTo["short"] == str(city_to):
							for c2 in cityTo["connections"]:
								if c2["dest"] == str(city_from):
									cityTo['connections'].remove(c2)

									response = make_response( json.dumps(cityFrom), 200, {'content-type':'application/json'})
									return response

	#return '\nNie znaleziono polaczenia pomiedzy podanymi miastami.\nZ: %s, DO: %s\n' % (city_from, city_to), 404
	response = make_response( 'Nie znaleziono polaczenia pomiedzy podanymi miastami.\nZ: %s, DO: %s\n' % (city_from, city_to), 
								404, {'content-type':'text/html'})
	return response

### --------------------------------------------------DIJKSTRA------------------------------------------------

### zwroci liste zawierajaca pary (numer miasta,skrot)
def compress_cities(cities):
	result = []
	for city in cities:
		new_city = {}
		new_city['id'] = city['id']
		new_city['short'] = city['short']
		result.append(new_city)

	return result

### zwraca numer id miasta dla jego skrotu
def get_city_id(cities, short):
	result = -1
	for city in cities:
		if city['short'] == short:
			#result = city['id']
			result = cities.index(city)

	return result

### zwraca numer id miasta dla jego pelnej nazwy
def get_city_id_by_name(cities, name):
	result = -1
	for city in cities:
		if city['name'] == name:
			#result = city['id']
			result = cities.index(city)

	return result

### zwraca skrot miasta dla jego numeru id
def get_short_by_id(cities, city_id):
	result = ''
	for city in cities:
		if city['id'] == city_id:
			result = city['short']
	return result

### zwraca nazwe miasta dla jego numeru id
def get_name_by_id(cities, city_id):
	result = ''
	for city in cities:
		if city['id'] == city_id:
			result = city['name']
	return result


### zwraca odleglosc pomiedzy 2 miastami na podstawie ich numerow id
def get_distance_by_id(cities, city_id1, city_id2):
	result = -1
	for city in cities:
		if city['id'] == city_id1:
			for c in city['connections']:
				if c['dest'] == get_short_by_id(cities,city_id2):
					result = c['dist']

	return result

### pobiera sasiadow dla danego miasta
### i zwraca liste tych sasiadow jako numery id
def get_neighbours(cities, city_id):
	neighbours = []
	compressed_cities = compress_cities(cities)

	for city in cities:					### szukam miasta, dla ktorego chce pobrac sasiadow
		if city['id'] == city_id:
			for j in city['connections']:
				short = j['dest']
				for c in compressed_cities:
					if c['short'] == short:
						neighbours.append(c['id'])

	return neighbours

### funkcja znajdujaca najkrotsza droge miedzy wierzcholkami w grafie wazonym
### dla przypadku wyszukiwania drogi miedzy miastami, miasta sa przedstawiane
###		jako ich numery id
###
### graf - zbior wszystkich wierzcholkow - lista
### n - liczba wierzcholkow
### start - wierzcholek zrodlowy (poczatek wyszukiwania)
### end - wierzcholek docelowy
def dijkstra(cities, n, start, end):

	S = []								#pusty zbior przetworzonych wierzcholkow
	Q = []								#zbior zawierajacy wszystkie wierzcholki (wypelniony ponizej)
	for i in range(n): 					#wierzcholki maja kolejne numery, wiec moge je 'dodac' w ten sposob
		Q.append(i)

	d = []
	p = []

	for i in range(n):
		d.append(100000)
		p.append(-1)

	d[start] = 0	#ustawienie kosztu dojscia do samego siebie - do zrodla, na zero

	sentinel = False
	while Q:

		lowest = 1000000
		for low in d:
			if low < lowest and d.index(low) in Q:
				lowest = low

		Q.remove(d.index(lowest))
		S.append(d.index(lowest))

		if sentinel == True:
			break

		neighbours = get_neighbours(cities, d.index(lowest))

		if neighbours is None:
			return None

		if end in neighbours:
			sentinel = True

		if sentinel is True:
			if end in Q:
				if d[end] > (lowest + get_distance_by_id(cities,d.index(lowest),end)):
					d[end] = lowest + get_distance_by_id(cities,d.index(lowest),end)
					p[end] = d.index(lowest)
		else:
			for neighbour in neighbours:	#to sa numery id
				if neighbour in Q:
					if d[neighbour] > (lowest + get_distance_by_id(cities,d.index(lowest),neighbour)):
						d[neighbour] = lowest + get_distance_by_id(cities,d.index(lowest),neighbour)
						p[neighbour] = d.index(lowest)

	przez = []
	through = []
	ps = end
	przez.append(get_name_by_id(cities,ps))

	while p[ps] != -1:
		przez.append(get_name_by_id(cities,p[ps]))
		ps = p[ps]
	for i in reversed(przez):
		through.append(i)

	print('-----------------------------------------')
	print('WYSZUKANO POLACZENIE:')
	print('Trasa z ' + get_short_by_id(cities,start) + ' do ' + get_short_by_id(cities,end) + ' wynosi: ' + str(d[end]))
	print('>>WPTransport<< ma nadzieje, że podroz minela przyjemnie oraz zaprasza na kolejne przygody.')
	print('-----------------------------------------')

	new_route = {'distance':d[end],'through':through}
	return new_route

if __name__ == '__main__':
	app.run(host='0.0.0.0')
