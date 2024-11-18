# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_hard_to_guess_string'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:admin@localhost/newsWeb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

