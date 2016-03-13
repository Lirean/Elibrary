from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response       
from . import main
from .. import db
from flask.ext.login import current_user
from ..models import User, Book, Author
from .forms import AddBookForm, RemoveBookForm, SearchForm


@main.route('/search_results/<query>')
def search_results(query):
    results = []
    results += Book.query.whoosh_search(query, current_app.config['MAX_SEARCH_RESULTS']).all()
    author_results = Author.query.whoosh_search(query, current_app.config['MAX_SEARCH_RESULTS']).all()
    for author in author_results:
        for book in author.books:
            results.append(book)
    return render_template('search_results.html', query=query, results=results)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    pagination = Book.query.order_by(Book.id).paginate(
    page, per_page=current_app.config['ELIBRARY_BOOKS_PER_PAGE'],
    error_out=False)
    books = pagination.items
    if form.validate_on_submit():
        return redirect(url_for('.search_results', query=form.search.data))
    return render_template('index.html', books=books,
    	                   pagination=pagination, form=form)


@main.route('/book/<int:id>', methods=['GET', 'POST'])
def book(id):
    book = Book.query.get_or_404(id)
    form = AddBookForm(prefix="form")
    form2 = RemoveBookForm(prefix="form2")
    if form.validate_on_submit() and form.submit.data:
        current_user.books.append(book)
        flash('Book was added to your library')
        return redirect(url_for('.book', id=book.id))
    if form2.validate_on_submit() and form2.submit.data:
        current_user.books.remove(book)
        flash('Book was removed from your library')
        return redirect(url_for('.book', id=book.id))        
    return render_template('book.html', books=[book], form=form,form2=form2)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)