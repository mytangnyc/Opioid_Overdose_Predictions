from flask import Flask, render_template, url_for, jsonify



application = Flask(__name__)



@application.route('/')
def index():
    return render_template('landing.html')

@application.route('/spacer1')
def spacer1():
    return render_template('spacer1.html')

@application.route('/spacer1a')
def spacer1a():
    return render_template('spacer1a.html')

@application.route('/spacer2')
def spacer2():
    return render_template('spacer2.html')

@application.route('/spacer3')
def spacer3():
    return render_template('spacer3.html')

@application.route('/spacer4')
def spacer4():
    return render_template('spacer4.html')

@application.route('/spacer5')
def spacer5():
    return render_template('spacer5.html')

@application.route('/landing')
def landing():
    return render_template('landing.html')

@application.route('/sales1')
def sales1():
    return render_template('sales1.html')

@application.route('/sales2')
def sales2():
    return render_template('sales2.html')

@application.route('/sales3')
def sales3():
    return render_template('sales3.html')

@application.route('/clusters')
def clusters():
    return render_template('clusters.html')

@application.route('/ml')
def ml():
    return render_template('ml.html')

@application.route('/crimerates')
def crimerates():
    return render_template('crimerates.html')

@application.route('/alcohol')
def alcohol():
    return render_template('alcohol.html')

@application.route('/income1')
def income1():
    return render_template('income1.html')

@application.route('/income2')
def income2():
    return render_template('income2.html')

if __name__ == '__main__':
    application.run()
