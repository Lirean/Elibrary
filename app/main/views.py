from flask import render_template, abort, request, current_app
from . import main
from ..models import User, Book


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Book.query.order_by(Book.id).paginate(
    page, per_page=current_app.config['FLASKY_BOOKS_PER_PAGE'],
    error_out=False)
    books = pagination.items
    return render_template('index.html', books=books,
    	                   pagination=pagination)

@main.route('/book/<int:id>')
def book(id):
	book = Book.query.get_or_404(id)
	return render_template('book.html', books=[book])

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)