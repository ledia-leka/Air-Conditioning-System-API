from dbm import dumb
from enum import unique
from http.client import responses
from unicodedata import name
from flask import Flask, jsonify, abort
from flask import request, make_response
from flask_restful import Api, Resource, reqparse
from werkzeug.http import HTTP_STATUS_CODES
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
 #Db table
class orac(db.Model):
    name = db.Column(db.String, primary_key=True, nullable = False)
    target_t = db.Column(db.Integer, nullable=False)
    current_t = db.Column(db.String(3), nullable=False)
    target_h = db.Column(db.String(3), nullable=False)
    current_h = db.Column(db.String(3), nullable=False)

#Can only be added once because we cannot have duplicate values

#db.session.add(orac(name="ac-or1", target_t=20,current_t="18",target_h="40%",current_h="35%"))
#db.session.add(orac(name="ac-or2", target_t=17,current_t="22",target_h="38%",current_h="30%"))
#db.session.add(orac(name="ac-or3", target_t=16,current_t="19",target_h="32%",current_h="36%"))
#db.session.add(orac(name="ac-or4", target_t=13,current_t="11",target_h="29%",current_h="34%"))
#db.session.commit()


#Error codes - error handling
@app.errorhandler(400)
def handle_400(_error):
    return jsonify({'There is an error' : 'Bad request; Server cannot or will not process'}),400

@app.errorhandler(404)
def handle_404(_error):
    return jsonify({'There is an error' : 'Not found'}),404

@app.errorhandler(500)
def handle_500(_error):
    return jsonify({'There is an error' : 'Sorry! Internal Server Error is occurring. Anyway, check your input'}),500


#Welcome to OR AC Api
@app.route("/index", methods = ['GET'])
def welcome():
    try:
        return jsonify("Hello! This is an OR AC System Api")
    except Exception as e:
        if "not found" in str(e):
            abort(404)
        return (str(e))


#Show current humidity in the OR
@app.route("/current-humidity/<ac_id>", methods = ['GET'])
def c_humidity(ac_id):
    try:
        result = orac.query.get(ac_id)
        humidity = result.current_h
        return jsonify("current_humidity: " + humidity)
    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        return (str(e))


#Show target humidity in the OR
@app.route("/target-humidity/<ac_id>", methods = ['GET'])
def t_humidity(ac_id):
    try:
        result = orac.query.get(ac_id)
        humidity = result.target_h
        return jsonify("target_humidity: " + humidity)
    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        return (str(e))


#Show current temperature in the OR
@app.route("/current-temp/<ac_id>", methods = ['GET'])
def c_temp(ac_id):
    try:
        result = orac.query.get(ac_id)
        celsius = result.current_t
        fahrenheit = str(int(((int(celsius) *9 / 5) + 32))) +"°F"      #Converts to °F
        return jsonify("Current_temp in Celsius: "+ str(celsius)+"°C","Current_temp in Fahrenheit: "+fahrenheit)
    except Exception as e:
            if "invalid literal" or "out of range" in str(e):
                abort(500)
            elif "not found" in str(e):
                abort(404)
            return (str(e))


#Show target temparature in the OR
@app.route("/target-temp/<ac_id>", methods = ['GET'])
def t_temp(ac_id):
    try:
        result = orac.query.get(ac_id)
        celsius = result.target_t
        fahrenheit = str(int(((int(celsius) *9 / 5) + 32))) +"°F"      #Converts to °F
        return jsonify("Target_temp in Celsius: "+ str(celsius)+"°C","Target_temp in Fahrenheit: "+fahrenheit)
    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        return (str(e))

#List all the sets of AC
@app.route("/presets", methods = ['GET'])
def presets():
    try:
        total =[]
        result = orac.query.order_by('name')
        for ac in result:
            to_json = {'name': ac.name,
            'target_t': ac.target_t,
            'current_t': ac.current_t,
            'target_h' : ac.target_h,
            'current_h': ac.current_h
            }
            total.append(to_json)
        return jsonify(total)
    except Exception as e:
        if "not found" in str(e):
            abort(404)
        elif "Bad request" in str(e):
            abort(400)
        return (str(e))

#Update the value of target temperature
@app.route("/temperature_update/<ac_id>", methods = ['PUT'])
def update_t_temp(ac_id):
    try:
        result = orac.query.get(ac_id)
        if(int(request.json['target_temperature']) >= 5):
            if( int(request.json['target_temperature']) <= 20):
               result.target_t = request.json['target_temperature']
               db.session.commit()
            else: return ("The input is beyond limits. Input should be between 5 and 20.")
        else: return ("The input is beyond limits. Input should be between 5 and 20")
        fahrenheit = str(int(((int(result.target_t) *9 / 5) + 32))) +"°F"
        to_json= {"AC name is ": result.name,
        "UPDATED target temp in Celsius: ": result.target_t,
        "in Fahrenheit:" : fahrenheit }
        return jsonify(to_json )
    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        return (str(e))

#Update the value of target humidity
@app.route("/update_humidity/<ac_id>", methods = ['PUT'])
def update_t_humidity(ac_id):
    try:
        result = orac.query.get(ac_id)
        result.target_h = request.json['target_humidity']
        db.session.commit()
        to_json= {"AC name is ": result.name,
        "UPDATED target humidity is: ": result.target_h}
        return jsonify(to_json )
    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        return (str(e))

#Create new AC set
@app.route("/create", methods = ['POST'])
def create_preset():
    try:
        new_ac= orac(name=request.json['ac_id'], target_t=request.json['target_temperature'], target_h = request.json['target_humidity'], current_t= "15", current_h="35%")
        db.session.add(new_ac)
        db.session.commit()
        return presets()

    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        elif "Bad request" in str(e):
            abort(400)
        return (str(e))

#Manage and update AC set
@app.route("/manage_set/<ac_id>", methods = ['PUT'])
def manage_set(ac_id):
    try:
        result = orac.query.get(ac_id)
        #Temp cannot be less than 5 of more than 20
        if(int(request.json['target_temperature']) >= 5):
                if(int(request.json['target_temperature']) <= 20):
                  result.name= request.json['ac_id']
                  result.target_t = request.json['target_temperature']
                  result.target_h = request.json['target_humidity']
                  db.session.commit()
                else: return ("The input is beyond limits")
        else: return ("The input is beyond limits")
        to_json= {"AC name is ": result.name,
        "Target temp: ": result.target_t,
        "Target humidity" : result.target_h,
        "Current temperature:": result.current_t,
        "Current humidity:": result.current_h
         }
        return jsonify(to_json)
    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        return (str(e))



#Remove AC of choice
@app.route("/remove/<ac_id>", methods = ['DELETE'])
def remove_preset(ac_id):
    try:
        result = orac.query.get_or_404(ac_id)
        db.session.delete(result)
        db.session.commit()
        return jsonify("Deleted successfully")
    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        return (str(e))

#Activate one of the listed ACs
@app.route("/activate/<ac_id>", methods = ['GET'])
def activate(ac_id):
    try:
        result = orac.query.get(ac_id)
        to_json= {"Activated AC is ": result.name,
        "Target temperature is: ": result.target_t,
        "Target humidity is: ": result.target_h,
        "Current temperature is: ": result.current_t,
        "Current humididty is: ": result.current_h}
        return jsonify(to_json )
    except Exception as e:
        if "invalid literal" or "out of range" in str(e):
            abort(500)
        elif "not found" in str(e):
            abort(404)
        return (str(e))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)