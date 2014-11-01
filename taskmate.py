from flask import Flask, render_template, request
import requests

app = Flask(__name__)

YO_API_TOKEN = 'b0651284-6164-485d-99ee-fa95a8f4f13a'

@app.route('/') 
def index():
   return render_template('home.html')

@app.route('/create') 
def create():
	template_values = {}
	eventname = request.args.get('eventname')
	eventdescription = request.args.get('eventdescription')

	template_values['eventname'] = eventname
	template_values['eventdescription'] = eventdescription
    
	return render_template('create.html', values=template_values)

@app.route('/yo')
def yo():
	template_values = {}
	return render_template('yo.html', values=template_values)

@app.route('/yo/send')
def yo_request():
	username = request.args.get('username')
	template_values = {'username':username}
	requests.post("http://api.justyo.co/yo/", data={'api_token': YO_API_TOKEN,'username':username})
	return render_template('yo.html', values=template_values)

if __name__ == "__main__":
	app.run(debug=True, port=8000)