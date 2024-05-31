from .database import db 
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class Librarian(db.Model) :
    __tablename__ = "librarian"
    username = db.Column(db.String(50), primary_key = True, nullable = False, unique = True)
    password = db.Column(db.String(50), primary_key = True, nullable = False, unique = True)


class User(db.Model) :
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    username = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(256), nullable = False)
    is_admin = db.Column(db.Boolean(), default = False)

    def __init__(self, username, password, is_admin = False) :
        self.username = username
        self.password = password
        self.is_admin = is_admin
    
    def check_password(self, p) :
        return check_password_hash(self.password, p)
    

class Books(db.Model) :
    __tablename__ = "books"
    book_id = db.Column(db.Integer, primary_key = True, autoincrement = True, unique = True, nullable = False)
    name = db.Column(db.String(100), nullable = False, unique = True)
    link = db.Column(db.String(256), nullable = False, unique = True)
    author = db.Column(db.String(200), nullable = False)
    date_added = db.Column(db.String(100), nullable = False, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __init__(self, name, link, author) :
        self.name = name
        self.link = link
        self.author = author

class Sections(db.Model) :
    __tablename__ = "sections"
    section_id = db.Column(db.Integer, primary_key=True, autoincrement = True, nullable = False)
    name = db.Column(db.String(50), nullable = False, unique = True)
    description = db.Column(db.String(1000), nullable = False)
    date_created = db.Column(db.String(100), nullable = False, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def  __init__(self, name, description) :
        self.name = name
        self.description = description

class RequestedBooks(db.Model) :
    __tablename__ = "requested_books"
    user_id = db.Column(db.Integer, primary_key = True, nullable = False)
    book_id = db.Column(db.Integer, primary_key = True, nullable = False)
    days_requested = db.Column(db.Integer, nullable = False)

    def __init__(self, user_id, book_id, days_requested) :
        self.user_id = user_id
        self.book_id = book_id
        self.days_requested = days_requested

class IssuedBooks(db.Model) :
    __tablename__ = "issued_books"
    user_id = db.Column(db.Integer, primary_key = True, nullable = False)
    book_id = db.Column(db.Integer, primary_key = True, nullable = False)
    date_issued = db.Column(db.String(100), nullable = False, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    date_return = db.Column(db.String(100), nullable = False)

    def __init__(self, user_id, book_id, num_days) :
        self.user_id = user_id
        self.book_id = book_id
        self.date_return = (datetime.now() + timedelta(days=int(num_days))).strftime("%Y-%m-%d %H:%M:%S")

class BooksSections(db.Model) :
    __tablename__ = "books_sections"
    book_id = db.Column(db.Integer, primary_key = True, nullable = False)
    section_id = db.Column(db.Integer, primary_key = True, nullable = False)  

    def __init__(self, book_id, section_id) :
        self.book_id = book_id
        self.section_id = section_id

