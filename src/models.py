from enum import unique
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    username = db.Column(db.String(15), unique = True, nullable= False)
    favorite = db.relationship("Favorite", backref="user", uselist=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable= False)
    name = db.Column(db.String(50), nullable= False)
    nature = db.Column(db.String(50), nullable= False)
    nature_id = db.Column(db.Integer, nullable= False)
    __table_args__=(db.UniqueConstraint(
        "user_id",
        "name",
        name="debe_tener_uno_solo_por_lista"
    ),)

    def __repr__(self):
        return f"<object favorite> f{self.id}"

    def serialize(self):
        return {
            "id" : self.id,
            "user": self.user_id,
            "name": self.name,
            "nature": self.nature,
            "nature_id": self.nature_id
        }
   

class People(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(30), unique=True, nullable= False)
    eye_color = db.Column(db.String(10))
    hair_color = db.Column(db.String(10))
    gender = db.Column(db.String(8))
    birth_year = db.Column(db.String(30))
    height = db.Column(db.Integer)
    skin_color = db.Column(db.String(30))

    def __repr__(self):
        return f"<object people>{self.name}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "eye_color": self.eye_color,
            "hair_color": self.hair_color,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "height": self.height,
            "skin_color": self.skin_color
        }


class Planets(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(20), unique = True, nullable =False)
    population = db.Column(db.String(30))
    climate = db.Column(db.String(30))
    gravity = db.Column(db.String(30))
    rotation_period = db.Column(db.Integer)
    orbital_period = db.Column(db.Integer)
    diameter = db.Column(db.Integer)

    def __repr__(self):
        return f"<object planet>{self.name}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "climate": self.climate,
            "gravity": self.gravity,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "diameter": self.diameter
        }