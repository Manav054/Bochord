import numpy as np
import pandas as pd
from sqlalchemy import func, select
from functools import wraps
from flask import redirect, url_for, flash, request, render_template, session
from .models import *
from app import app
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Bright6
from bokeh.embed import components

def get_requested_books_count(user_id):
    return db.session.query(func.count(RequestedBooks.book_id)).filter(RequestedBooks.user_id == user_id).scalar()

def days_difference(s) :
        date_object = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        difference = date_object - now
        return difference.days

def check_date(s) :
        date_object = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        if now > date_object :
            return True
        return False

def auth_required(func) :
    @wraps(func)
    def inner(*args, **kwargs) :
        if 'user_id' not in session or session['user_id'] is None :
            flash("please login to continue!!")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if ('is_admin' not in session and 'user_id' not in session) or (session['is_admin'] is None or session['user_id'] is None):
            flash("Please login to continue!")
            return redirect(url_for('admin'))
        return func(*args, **kwargs)
    return inner

@app.route("/")
@auth_required
def index() :
    return render_template("index.html", user = User.query.get(session['user_id']))


@app.route("/admin")
def admin() :
    return render_template("admin.html")

@app.route("/admin", methods=["POST"])
def admin_post() :
    username=request.form.get('username')
    password=request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if(username!=user.username or user.check_password(password)):
        flash('Please check your login information!')
        return redirect(url_for("admin"))
    session["is_admin"] = True
    session["user_id"] = user.user_id
    return redirect(url_for('librarian_section'))

@app.route("/login")
def login() :
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post() :
    username=request.form.get('username')
    password=request.form.get('password')
    user=User.query.filter_by(username=username).first()
    if not user :
        flash('User does not exist!!')
        return redirect(url_for('login'))
    if not user.check_password(password) :
        flash("Incorrect password!!")
        return redirect(url_for('login'))
    
    session['user_id']=user.user_id
    return redirect(url_for('user_book'))

@app.route("/register")
def register() :
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_post() :
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user is None :
        password_hash = generate_password_hash(password)
        newUser = User(username=username, password=password_hash)
        db.session.add(newUser)
        db.session.commit()
        flash("User created successfully! Please login!")
        return redirect(url_for('login'))
    else:
        flash("Username already exists!! Please try again with a different username.")
        return redirect(url_for('register'))
    
@app.route("/user/books")
@auth_required
def user_book() :
    books = db.session.query(Books, Sections).join(BooksSections, Books.book_id==BooksSections.book_id).join(Sections, BooksSections.section_id == Sections.section_id).order_by(Books.date_added.desc()).all()
    return render_template('book-user.html', books = books)

@app.route('/user/section')
@auth_required
def user_section() :
    sections=Sections.query.order_by(Sections.date_created.desc()).all()
    return render_template('section-user.html',sections=sections)

@app.route('/user/<string:section_name>/view')
@auth_required
def view_section_user(section_name) :
    section = Sections.query.filter_by(name=section_name).first()
    section_id = section.section_id
    books_in_section = db.session.query(Books).join(BooksSections, Books.book_id == BooksSections.book_id).filter(BooksSections.section_id == section_id).order_by(Books.date_added.desc()).all()
    return render_template("view-section-user.html", books=books_in_section, section_name=section_name)

@app.route("/user/<int:book_id>/rent")
@auth_required
def rent(book_id) :
    user_id = User.query.get(session['user_id']).user_id
    ib = IssuedBooks.query.filter_by(user_id = user_id, book_id=book_id).first()
    if ib :
        flash("You have already rented this book.")
        return redirect(url_for('profile_user'))
    return render_template('rent.html', book = Books.query.get(book_id), user = User.query.get(session['user_id']))

@app.route("/user/<int:book_id>/rent", methods = ["POST"])
@auth_required
def rent_post(book_id) :
    days = request.form.get("days")
    user_id = User.query.get(session['user_id']).user_id
    rb = RequestedBooks.query.filter_by(user_id=user_id, book_id=book_id).first()
    if rb :
        flash("You have already requested this book.")
        return redirect(url_for('user_book'))
    
    count = get_requested_books_count(user_id)
    if count >= 7 :
        flash("A user can only rent upto 7 books!!")
        return redirect(url_for('user_book'))

    newRequestedBooks = RequestedBooks(user_id=user_id, book_id=book_id, days_requested=days)
    db.session.add(newRequestedBooks)
    db.session.commit()
    flash("Your request  has been sent to the librarian for approval!")
    return redirect(url_for('user_book'))

@app.route("/user/return/<int:book_id>")
@auth_required
def Return(book_id) :
    user_id = User.query.get(session['user_id']).user_id
    issuedBook = IssuedBooks.query.filter_by(user_id=user_id, book_id=book_id).one()
    db.session.delete(issuedBook)
    db.session.commit()
    flash("The book is returned successfully.")
    user_id = User.query.get(session['user_id']).user_id
    ib = db.session.query(Books, IssuedBooks).join(IssuedBooks, Books.book_id==IssuedBooks.book_id).filter(IssuedBooks.user_id==user_id).all()
    return render_template('profile-user.html', ib = ib, difference=days_difference)

@app.route("/user/profile")
@auth_required
def profile_user() :
    user_id = User.query.get(session['user_id']).user_id
    issue = IssuedBooks.query.all()
    for i in issue :
        if check_date(i.date_return) :
            di = IssuedBooks.query.filter_by(user_id=i.user_id, book_id = i.book_id).one()
            db.session.delete(di)
            db.session.commit()
    
    ib = db.session.query(Books, IssuedBooks).join(IssuedBooks, Books.book_id==IssuedBooks.book_id).filter(IssuedBooks.user_id==user_id).all()
    return render_template('profile-user.html', ib = ib, difference=days_difference)

@app.route("/user/search", methods=["GET", "POST"])
@auth_required
def search_results():
    if request.method == "POST":
        parameter = request.form.get("parameter")
        q = request.form.get("query")
        if parameter == "name":
            results = db.session.query(Books, Sections).join(BooksSections, Books.book_id == BooksSections.book_id).join(Sections, Sections.section_id == BooksSections.section_id).filter(Books.name.like("%" + q + "%")).order_by(Books.date_added.desc()).all()
        elif parameter == "genre":
            results = db.session.query(Books, Sections).join(BooksSections, Books.book_id == BooksSections.book_id).join(Sections, Sections.section_id == BooksSections.section_id).filter(Sections.name.like("%" + q + "%")).order_by(Books.date_added.desc()).all()
        else:
            results = db.session.query(Books, Sections).join(BooksSections, Books.book_id == BooksSections.book_id).join(Sections, Sections.section_id == BooksSections.section_id).filter(Books.author.like("%" + q + "%")).order_by(Books.date_added.desc()).all()
        return render_template("search-results.html", results=results)
    return render_template("search-form.html")

@app.route("/librarian/sections")
@admin_required
def librarian_section() :
    return render_template('section-admin.html', sections=Sections.query.order_by(Sections.date_created.desc()).all())

@app.route("/librarian/books")
@admin_required
def librarian_book() :
    books = db.session.query(Books, Sections).join(BooksSections, Books.book_id==BooksSections.book_id).join(Sections, BooksSections.section_id == Sections.section_id).order_by(Books.date_added.desc()).all()
    return render_template("book-admin.html", books=books)

@app.route("/librarian/section/add")
@admin_required
def add_section() :
    return render_template('add-section.html')

@app.route("/librarian/section/add", methods=["POST"])
@admin_required
def add_section_post() :
    name = request.form.get('name')
    description = request.form.get('description')
    section = Sections.query.filter_by(name=name).first()
    if section is not None :
        flash("This section already exists!")
        return redirect(url_for('add_section'))
    else :
        newSection = Sections(name=name, description=description)
        db.session.add(newSection)
        db.session.commit()
        flash(f"{name} has been added to the Bochord.", "success")
        return redirect(url_for('librarian_section'))

@app.route("/librarian/<string:section_name>/view")
@admin_required
def view_section_librarian(section_name):
    section = Sections.query.filter_by(name=section_name).first()
    section_id = section.section_id
    books_in_section = db.session.query(Books).join(BooksSections, Books.book_id == BooksSections.book_id).filter(BooksSections.section_id == section_id).order_by(Books.date_added.desc()).all()
    return render_template("view-section-admin.html", books=books_in_section, section_name=section_name)

@app.route("/librarian/<string:section_name>/<int:book_id>/delete")
@admin_required
def delete_book_from_sections(section_name, book_id):
    b = Books.query.filter_by(book_id=book_id).first()
    s = Sections.query.filter_by(name=section_name).first()
    sb = BooksSections.query.filter_by(book_id=b.book_id, section_id=s.section_id).all()
    ib = IssuedBooks.query.filter_by(book_id=b.book_id).all()
    rb = RequestedBooks.query.filter_by(book_id=b.book_id).all()
    if b is not None:
        db.session.delete(b)
        for item in sb:
            db.session.delete(item)
        for item in ib:
            db.session.delete(item)
        for item in rb:
            db.session.delete(item)
        db.session.commit()

        flash(f"The book {b.name} has been deleted!")
        return redirect(url_for("view_section_librarian", section_name=section_name))
    else :
        flash(f"This book does not exist!!")
        return redirect(url_for("view_section_librarian", section_name=section_name))
    
@app.route("/librarian/<int:book_id>/delete")
@admin_required
def delete_book_from_books(book_id):
    b = Books.query.filter_by(book_id=book_id).first()
    sb = BooksSections.query.filter_by(book_id=b.book_id).all()
    ib = IssuedBooks.query.filter_by(book_id=b.book_id).all()
    rb = RequestedBooks.query.filter_by(book_id=b.book_id).all()
    if b is not None:
        db.session.delete(b)
        for item in sb:
            db.session.delete(item)
        for item in ib:
            db.session.delete(item)
        for item in rb:
            db.session.delete(item)
        db.session.commit()
        flash(f"The book {b.name} has been deleted!")
        return redirect(url_for("librarian_book"))
    else :
        flash(f"This book does not exist!!")
        return redirect(url_for("librarian_book"))

@app.route("/librarian/<string:section_name>/add_book")
@admin_required
def add_book(section_name) :
    return render_template("add-book.html", section_name = section_name)

@app.route("/librarian/<string:section_name>/add_book", methods = ["POST"])
@admin_required
def add_book_post(section_name) :
    book_name = request.form.get("name")
    author = request.form.get("author")
    link = request.form.get("link")
    book = Books.query.filter_by(name = book_name).first()
    if book is None :
        section = Sections.query.filter_by(name=section_name).first()
        section_id = section.section_id
        newBook = Books(name=book_name, author=author, link=link)
        db.session.add(newBook)
        db.session.commit()

        book = Books.query.filter_by(name=book_name).first()
        book_id = book.book_id
        newBooksSections = BooksSections(book_id=book_id, section_id=section_id)
        db.session.add(newBooksSections)
        db.session.commit()

        flash(f"The book has been added to the {section_name} section.")
        return redirect(url_for('view_section_librarian', section_name = section_name)) 
    else :
        flash(f"This book already exists in {section_name} section!!")
        return redirect(url_for('add_book', section_name=section_name))
    
@app.route("/librarian/<int:section_id>/delete_section")
@admin_required
def delete_section(section_id) :
    SecsBooks = BooksSections.query.filter_by(section_id=section_id).first()
    if SecsBooks is None:
        s = Sections.query.filter_by(section_id=section_id).first()
        db.session.delete(s)
        db.session.commit()
        flash(f"Section has been deleted!")
        return redirect(url_for("librarian_section"))
    else :
        flash(f"Section is not empty. Please empty the section first!")
        return redirect(url_for("librarian_section"))

@app.route('/librarian/user-requests')
@admin_required
def requests() :
    rbs = db.session.query(User, Books).join(RequestedBooks, RequestedBooks.user_id==User.user_id).join(Books, RequestedBooks.book_id==Books.book_id).all()
    return render_template("request.html", rbs= rbs)

@app.route("/grant/<int:user_id>/<int:book_id>")
@admin_required
def grant(user_id, book_id) :
    rb = RequestedBooks.query.filter_by(user_id=user_id, book_id=book_id).first()
    newissue = IssuedBooks(user_id = rb.user_id, book_id=rb.book_id, num_days=rb.days_requested)
    db.session.add(newissue)
    db.session.delete(rb)
    db.session.commit()
    flash('The book has been granted to the user.')
    return redirect(url_for('requests'))

@app.route("/revoke/<int:user_id>/<int:book_id>")
@admin_required
def revoke(user_id, book_id) :
    rb = RequestedBooks.query.filter_by(user_id=user_id, book_id=book_id).first()
    db.session.delete(rb)
    db.session.commit()
    flash('The request has been denied.')
    return redirect(url_for('requests'))

@app.route("/revoke/stats/<int:user_id>/<int:book_id>")
@admin_required
def revoke_stats(user_id, book_id) :
    ib = IssuedBooks.query.filter_by(user_id=user_id, book_id=book_id).first()
    db.session.delete(ib)
    db.session.commit()
    flash('The book has been revoked!')
    return redirect(url_for('stats'))

@app.route("/librarian/stats")
@admin_required
def stats() :
    ib = db.session.query(User, Books, IssuedBooks).join(Books, Books.book_id==IssuedBooks.book_id).join(User, User.user_id==IssuedBooks.user_id).all()
    return render_template('stats-admin.html', ib = ib, difference=days_difference)

@app.route("/librarian/stats", methods=["POST"])
@admin_required
def stats_post() :
    option = request.form.get("option")
    if option == "1" :
        return redirect(f"/librarian/stats/{int(option)}")
    elif option == "2" :
        return redirect(f"/librarian/stats/{int(option)}")
    else : 
        pass

@app.route("/librarian/stats/<int:option>")
@admin_required
def show_statistics(option):
    ib = db.session.query(User, Books, IssuedBooks).join(Books, Books.book_id==IssuedBooks.book_id).join(User, User.user_id==IssuedBooks.user_id).all()
    if option == 1 :
        booksusers = db.session.query(User.username, func.count(IssuedBooks.book_id)).join(IssuedBooks, User.user_id == IssuedBooks.user_id).group_by(IssuedBooks.user_id).all()
        users, num_books = [], []
        for row in booksusers :
            users.append(row[0])
            num_books.append(row[1])
        p = figure(x_range=users, height=350, title="No. of books VS Users", y_range=(0,9), toolbar_location=None, tools="")
        p.vbar(x=users, top=num_books, width=0.6)
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        script, div = components(p)
        return render_template("show-stats.html", div = div, script = script, ib = ib, difference=days_difference)
    if option == 2 :
        secdist = db.session.query(Sections.name, func.count(BooksSections.book_id)).join(BooksSections, Sections.section_id == BooksSections.section_id).group_by(BooksSections.section_id).all()
        sections, num_books = [], []
        for row in secdist :
            sections.append(row[0])
            num_books.append(row[1])
        p = figure(x_range=sections, height=350, title="No. of books VS Sections", y_range=(0,9), toolbar_location=None, tools="")
        p.vbar(x=sections, top=num_books, width=0.6)
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        script, div = components(p)
        return render_template("show-stats.html", div = div, script = script, ib = ib, difference=days_difference)

@app.route("/librarian/stats/<int:option>", methods = ["POST"])
@admin_required
def show_statistics_post(option):
    value = request.form.get("value")
    if value == "1" :
        return redirect(f"/librarian/stats/{int(value)}")
    elif value == "2" :
        return redirect(f"/librarian/stats/{int(value)}")
    else : 
        pass

@app.route("/logout")
def logout() :
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash("You have been logged out!!")
    return redirect(url_for("login"))