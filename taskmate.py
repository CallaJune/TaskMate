from flask_oauth import OAuth
from flask import Flask, render_template, request

app = Flask(__name__)

oauth = OAuth()
gtasks = oauth.remote_app('googletasks',
	base_url='https://www.googleapis.com/',
	request_token_url=None,
	access_token_url=None,
	authorize_url='/auth/tasks',
	consumer_key='805075416684-sm8ktm9sel14r7fv42tocdmpsk423fni.apps.googleusercontent.com',
	consumer_secret='p_4wg243g0N5seeG9sgxj1fz'
	)

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

if __name__ == "__main__":

	app.run(debug=True)