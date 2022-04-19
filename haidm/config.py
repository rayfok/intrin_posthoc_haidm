import os

basedir = os.path.abspath(os.path.dirname(__file__))

APPLICATION_ROOT = "/"
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "haidm.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
