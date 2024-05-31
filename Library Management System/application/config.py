import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config() :
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmetnConfig(Config) :
    SQLITE_DB_DIR = os.path.join(basedir, '../db_directory')
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "db.sqlite3")
    DEBUG = True
    SECRET_KEY = "yiakjcbkavcuaifaobcianpcohsgaipibsvibacapifh"
    SECRET_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "nogsifblkhfpag"
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_MAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None