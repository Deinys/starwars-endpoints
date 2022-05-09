"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import Favorite, People, Planets, db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']=os.environ.get('FLASK_APP_KEY')
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# metodos GET y POST de User
@app.route('/user', methods=['GET'])
@app.route('/user/<int:user_id>', methods=['GET'])
def handle_user(user_id = None):
    if user_id is None:
        users= User.query.all()
        users= list(map(lambda user: user.serialize(), users))
        return jsonify(users), 200
    else:
       user = User.query.filter_by(id=user_id).first()
       if user is not None:
           return jsonify(user.serialize()), 200
       else:
           return jsonify({
               "msg": "user is not found"
           }), 404 


@app.route('/user', methods=['POST'])
def create_user():
    request_body = request.json
    if not request_body.get("email") and not request_body.get("password") and not request_body.get("username"):
        return ({
            "msg": "error"
        }),400
    

    user = User(email=request_body["email"], password=request_body["password"], username=request_body["username"])    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.serialize()), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(error.args), 500 


# Metodo GET user/favorite
@app.route('/user/favorite', methods=['GET'])
@jwt_required()
def user_favorite():
    user_id = get_jwt_identity()
    favorites= Favorite.query.filter_by(user_id=user_id).all()
    if favorites != []:
        favorites= list(map(lambda favorite: favorite.serialize(), favorites))
        return jsonify(favorites),200
    else:
        return jsonify({
            "msg": "user has no favorites"
        }), 404


#Funcion login
@app.route('/login', methods=['POST'])
def crear_login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    username = request.json.get("username", None)
    if email is not None and password is not None and username is not None:
        user = User.query.filter_by(email=email, password=password, username=username).one_or_none()
        if user is not None:
            create_token = create_access_token(identity=user.id)
            return jsonify({
                "token": create_token,
                "user.id": user.id,
                "email": user.email
            }), 200
        else:
           return jsonify({
            "msg": "not found"
        }),404  
    else:
        return jsonify({
            "msg": "error"
        }),400 

    


# metodos GET, POST y DELETE de People
@app.route('/people', methods=['GET'])
@app.route('/people/<int:people_id>', methods=['GET'])     
def handle_people(people_id=None):
    if people_id is None:
        people = People.query.all()
        people = list(map(lambda person: person.serialize(), people))
        return jsonify(people)
    else:
        person = People.query.filter_by(id=people_id).first()
        if person is not None:
            return jsonify(person.serialize()), 200
        else:
            return jsonify({
                "msg": "people_is_not_found"
            }), 400



#metodos GET, POST y DELETE de planet
@app.route('/planets', methods=['GET'])
@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_planet(planet_id=None):
    if planet_id is None:
        planets = Planets.query.all()
        planets = list(map(lambda planet: planet.serialize(),planets))
        return jsonify(planets),200
    else:
        planet = Planets.query.filter_by(id=planet_id).first()
        if planet is not None:
            return jsonify(planet.serialize()),200
        else:
            return jsonify({
                "msg": "planet_is_not_found"
            }),500


#metodos de Favorite
@app.route('/favorite/<string:nature>/<int:nature_id>', methods=['POST', 'DELETE'])
@jwt_required()
def handle_favorite_planet(nature_id = None, nature = None):
   user_id = get_jwt_identity() 
   
   if nature is not None:
       #favorite planet

       if nature == "planet":
           favorite_planet = Planets.query.filter_by(id=nature_id).first()
           if favorite_planet is not None:

               #Metodo POST de favorite/planet 

               if request.method == 'POST':
                   request_body = request.json
                   if not request_body.get("name"):
                       return jsonify({
                           "msg": "error"
                           }),400
                   else:
                       planet_favorite = Favorite(name=request_body["name"], user_id=user_id, nature=nature, nature_id=nature_id)
                       try:
                           db.session.add(planet_favorite)
                           db.session.commit()
                           return jsonify(planet_favorite.serialize()),200
                       except Exception as error:
                           db.session.rollback()
                           return jsonify(error.args),500

                #Metodo DELETE de favorite/planet

               if request.method == 'DELETE':
                   delete_planet_favorite = Favorite.query.filter_by(nature_id=nature_id, user_id=user_id).first()
                   try: 
                       db.session.delete(delete_planet_favorite)
                       db.session.commit()
                       return jsonify(delete_planet_favorite.serialize()),200
                   except Exception as error:
                       db.session.rollback()
                       return jsonify(error.args), 500
           else:
               return jsonify({
                   "msg": "planet not found"
               }), 404

       #favorite people
                    
       if nature == "people":
           favorite_people = People.query.filter_by(id = nature_id).first()
           if favorite_people is not None:

               #Metodo POST

               if request.method == 'POST':
                   request_body= request.json
                   if not request_body.get("name"):
                       return jsonify({
                           "msg": "error"
                        }),400
                   else:
                       people_favorite= Favorite(name=request_body["name"], nature=nature, nature_id=nature_id, user_id= user_id)
                       try:
                           db.session.add(people_favorite)
                           db.session.commit()
                           return jsonify(people_favorite.serialize()),200
                       except Exception as error:
                           db.session.rollback()
                           return jsonify(error.args),500

               #Metodo DELETE

               if request.method == 'DELETE':
                   delete_people_favorite = Favorite.query.filter_by(nature_id=nature_id, user_id=user_id).first()
                   try:
                       db.session.delete(delete_people_favorite)
                       db.session.commit()
                       return jsonify(delete_people_favorite.serialize()), 200
                   except Exception as error:
                       db.session.rollback()
                       return jsonify(error.args),500
           else:
               return jsonify({
                   "msg": "people not found"
               }), 404   
   else:
        return jsonify({
            "msg": "error"
        }), 400 
  



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
