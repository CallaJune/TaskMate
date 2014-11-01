from flask import Flask, render_template, request

app = Flask(__name__)

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