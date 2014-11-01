from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
import requests

app = Flask(__name__)
app.config['GOOGLE_ID'] = "805075416684-sm8ktm9sel14r7fv42tocdmpsk423fni.apps.googleusercontent.com"
app.config['GOOGLE_SECRET'] = "p_4wg243g0N5seeG9sgxj1fz"
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)
YO_API_TOKEN = 'b0651284-6164-485d-99ee-fa95a8f4f13a'

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        return jsonify({"data": me.data})
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    return jsonify({"data": me.data})


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

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