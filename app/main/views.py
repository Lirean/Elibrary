from flask import render_template, abort
from . import main
from ..models import User, Book


@main.route('/', methods=['GET', 'POST'])
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)