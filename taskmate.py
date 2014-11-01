from flask import Flask, render_template, request
import requests
from flask_oauthlib.client import OAuth
app = Flask(__name__)

YO_API_TOKEN = 'b0651284-6164-485d-99ee-fa95a8f4f13a'

oauth = OAuth()
tasks = oauth.remote_app('tasks',
    consumer_key='805075416684-sm8ktm9sel14r7fv42tocdmpsk423fni.apps.googleusercontent.com',
    consumer_secret='p_4wg243g0N5seeG9sgxj1fz',request_token_params={'scope':['https://www.googleapis.com/auth/tasks']},
    base_url='https://www.googleapis.com/oauth2/v1',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token', 
    request_token_url=None
)

@app.route('/') 
def index():
   return render_template('home.html')

@app.route('/login')
def login():
	print tasks.authorize(callback=url_for('authorized',_external=True))
	return tasks.authorize(callback=url_for('authorized',_external=True))

@app.route('/login/authorized')
@tasks.authorized_handler
def authorized(resp):
	session['tasks_token'] = (resp['access_token'])
	user = tasks.get('userinfo')
	session['user_email'] = user.data['email']
	return user

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