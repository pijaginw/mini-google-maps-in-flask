# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, session, url_for, make_response, render_template
import json
import requests

app_url = '/pijaginw/findyourwayapp'
app = Flask(__name__)
app.secret_key = '8@*73fdr_1$*rtrp3*(()12a##'

#from werkzeug.debug import DebuggedApplication
#app.debug = True
#app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

@app.route(app_url + '/', methods=['GET', 'POST'])
def index():

	if request.method == 'GET':

		url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/cities"
		r = requests.get( url )

		try:
			data = r.json()
			response = make_response( render_template('findyourway_index.html', cities= data), 200 )
			return response
		except ValueError, e:
			response = make_response( render_template('flask_findyourway_error.html', error_msg= str(e)), 500 )
			return response

	elif request.method == 'POST':
		from_city = request.form.get('cityFrom')
		to_city = request.form.get('cityTo')
	
		trasa = { 'from': from_city, 'to': to_city }

		url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/routes"
		headers = {'content-type': 'application/json'}

		r = requests.post( url, data= json.dumps(trasa), headers= headers )

		print('-->Kod odpowiedzi: %s' % r.status_code)
		print('-->Tresc odpowiedzi: %s' % r.text)

		try:
			data = r.json()
			return render_template('flask_findyourway_route.html', city_from= str(data['from']), route_id= str(data['id']), 
									city_to= str(data['to']), distance= str(data['route']), through= data['through'])

		except ValueError, e:
			response = make_response( render_template('flask_findyourway_error.html', error_msg= str(e)), 500 )
			return response



@app.route(app_url + '/city', methods=['GET', 'POST'])
def add_new_city():

	if request.method == 'GET':
		return render_template('findyourway_add_city.html')

	elif request.method == 'POST':

		newcity_short = request.form.get('newcity_short')
		newcity_name = request.form.get('newcity_name')
		newcity_connections = request.form.get('newcity_connections')

		### usluga zajmuje sie walidacja danych
		new_city = {"short":newcity_short, "name":newcity_name, "connections":newcity_connections}

		url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/city"
		headers = { 'content-type': 'application/json' }

		r = requests.post( url, data= json.dumps(new_city), headers= headers )

		print('-->Kod odpowiedzi: %s' % r.status_code)
		print('-->Tresc odpowiedzi: %s' % r.text)

		if (r.status_code == str(304)) or (r.status_code == str(400)):
			response = make_response( render_template('flask_findyourway_error.html', error_msg= r.text), r.status_code )
			return response

		try:
			data = r.json()

			return render_template('flask_findyourway_new_city.html', 
									name= str(data['name']), short= str(data['short']),
									data= data, cityID= str(data['id']))

		except ValueError, e:
			response = make_response( render_template('flask_findyourway_error.html', error_msg= r.text), 500 )
			return response


@app.route('/pijaginw/findyourwayapp/city' + '/<int:city_id>', methods=['GET'])
def show_city(city_id):

	url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/city/" + str(city_id)

	r = requests.get( url )

	print('-->Kod odpowiedzi: %s' % r.status_code)
	print('-->Tresc odpowiedzi: %s' % r.text)

	if r.status_code == str(404):
		response = make_response( render_template('flask_findyourway_error.html', 
													error_msg= r.text), 404 )
		return response

	try:
		data = r.json()
		return render_template('flask_findyourway_edit_city.html', 
								name= str(data['name']), short= str(data['short']),
								data= data, cityID= city_id)

	except ValueError, e:
		response = make_response( render_template('flask_findyourway_error.html', 
													error_msg= r.text), int(r.status_code) )
		return response


@app.route('/pijaginw/findyourwayapp/city' + '/<int:city_id>', methods=['POST'])
def edit_city(city_id):

	new_name = request.form.get('new_name')
	new_connections = request.form.get('new_connections')

	data = {}
	if new_name != '':
		data["newName"] = new_name
	if new_connections != '':
		data["newConnections"] = new_connections

	url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/city/" + str(city_id)
	headers = { 'content-type': 'application/json' }

	r = requests.post( url, data= json.dumps(data), headers= headers )
	print('-->Kod odpowiedzi: %s' % r.status_code)
	print('-->Tresc odpowiedzi: %s' % r.text)


	if r.status_code == 304:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= r.text), 304 )
		return response
	if r.status_code == 400:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= r.text), 400 )
		return response
	
	try:
		data = r.json()
		return render_template('flask_findyourway_updated_city.html', 
								name= str(data['name']), short= str(data['short']),
								data= data, cityID= city_id)

	except ValueError, e:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= str(e)), 500 )
		return response



@app.route(app_url + '/city_del/<city_id>', methods=['POST'])
def delete_city(city_id):

	url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/city/" + str(city_id)

	r = requests.delete( url )

	print('-->Kod odpowiedzi: %s' % r.status_code)
	print('-->Tresc odpowiedzi: %s' % r.text)

	if r.status_code == 410:
		return render_template('flask_findyourway_city_removed.html')

	else:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= 'error'), 404 )
		return response


@app.route(app_url + '/cities', methods=['GET'])
def show_all_cities():

	url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/cities"
	r = requests.get( url )

	print('-->Kod odpowiedzi: %s' % r.status_code)
	print('-->Tresc odpowiedzi: %s' % r.text)

	try:
		data = r.json()
		return render_template('flask_findyourway_cities.html', cities= data)

	except ValueError, e:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= str(e)), 500 )
		return response


### ----POLACZENIA MIEDZY MIASTAMI----

@app.route(app_url + '/connections', methods=['GET'])
def show_connection_editor():

	url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/connections"
	r = requests.get( url )

	print('-->Kod odpowiedzi: %s' % r.status_code)
	print('-->Tresc odpowiedzi: %s' % r.text)

	try:
		data = r.json()
		return render_template('flask_findyourway_edit_connection.html', cities= data)

	except ValueError, e:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= str(e)), 500 )
		return response


@app.route(app_url + '/connections', methods=['POST'])
def edit_connection():

	cityFrom = request.form.get('cityFrom')
	cityTo = request.form.get('cityTo')
	newValue = request.form.get('newValue')

	if (cityFrom == '' and cityTo == '' and newValue == '') :
		return 'Nie podano danych do edycji polaczenia.\n', 304

	data = { "newValue": int(newValue) }

	url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/connections/" + str(cityFrom) + '/' + str(cityTo)
	headers = { 'content-type': 'application/json' }

	r = requests.put( url, data= json.dumps(data), headers= headers )
	print('-->Kod odpowiedzi: %s' % r.status_code)
	print('-->Tresc odpowiedzi: %s' % r.text)

	if r.status_code == 404:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= r.text), 404 )
		return response

	try:
		data = r.json()
		return render_template('flask_findyourway_updated_city.html', 
								name= str(data['name']), short= str(data['short']),
								data= data, cityID= str(data['id']))

	except ValueError, e:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= str(e)), 500 )
		return response


@app.route(app_url + '/connections_delete', methods=['POST'])
def delete_connection():

	cityFromDel = request.form.get('cityFromDel')
	cityToDel = request.form.get('cityToDel')

	if ( cityFromDel == '' and cityToDel == '' ) :
		return 'Nie podano danych do usuniecia polaczenia.\n', 304

	url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/connections/" + str(cityFromDel) + '/' + str(cityToDel)
	headers = { 'content-type': 'application/json' }

	r = requests.delete( url )
	print('-->Kod odpowiedzi: %s' % r.status_code)
	print('-->Tresc odpowiedzi: %s' % r.text)

	if r.status_code == 404:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= r.text), 404 )
		return response

	try:
		data = r.json()
		return render_template('flask_findyourway_updated_city.html', 
								name= str(data['name']), short= str(data['short']),
								data= data, cityID= str(data['id']))

	except ValueError, e:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= str(e)), 500 )
		return response

@app.route(app_url + '/routes/' + '<route_id>', methods=['GET'])
def show_route(route_id):

	url = "http://edi.iem.pw.edu.pl/pijaginw/findyourway/routes/" + str(route_id)
	r = requests.get( url )

	print('-->Kod odpowiedzi: %s' % r.status_code)
	print('-->Tresc odpowiedzi: %s' % r.text)

	if r.status_code == 404:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= r.text), 500 )
		return response

	try:
		data = r.json()
		return render_template('flask_findyourway_view_route.html', route= data)

	except ValueError, e:
		response = make_response( render_template('flask_findyourway_error.html', error_msg= str(e)), 500 )
		return response

if __name__ == '__main__':
	app.run(host='0.0.0.0')
