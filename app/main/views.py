from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response       
from . import main
from .. import db
from flask.ext.login import current_user, login_required
from ..models import User, Book, Author, Role, Year, Permission
from .forms import AddBookForm, RemoveBookForm, SearchForm, EditProfileAdminForm, AdminAddBookForm
from ..decorators import admin_required, permission_required


@main.route('/delete_book_admin/<int:id>')
@login_required
@permission_required(Permission.MODERATE_BOOKS)
def delete_book_admin(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    flash('The book has been deleted.')
    return redirect(url_for('.index'))


@main.route('/edit_book_admin/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE_BOOKS)
def edit_book_admin(id):
    book = Book.query.get_or_404(id)
    form = AdminAddBookForm()
    if form.validate_on_submit():
        authors = form.author.data.split(', ')
        for a in authors:
            if Author.query.filter_by(name=a).first() == None:
                db.session.add(Author(name=a))
                db.session.commit()
        y = Year.query.filter_by(year=form.year.data).first()
        if y is None:
            db.session.add(Year(year=form.year.data))
            db.session.commit()        
        book.name = form.name.data
        book.description = form.description.data
        book.year_id = Year.query.filter_by(year=form.year.data).first().id
        book.authors = []
        for a in authors:
            book.authors.append((Author.query.filter_by(name=a).first()))
        db.session.add(book)
        flash('The book has been updated.')
        return redirect(url_for('.book', id=book.id))
    form.name.data = book.name
    form.description.data = book.description
    form.year.data = Year.query.filter_by(id=book.year.id).first().year
    form.author.data = ', '.join([x.name for x in book.authors])
    return render_template('edit_book_admin.html', form=form, book=book)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/add_book_admin/', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book_admin():
    form = AdminAddBookForm()
    if form.validate_on_submit():
        book = Book()
        a = Author.query.filter_by(name=form.author.data).first()
        if a is None:
            db.session.add(Author(name=a))
            db.session.commit()
        y = Year.query.filter_by(year=form.year.data).first()
        if y is None:
            db.session.add(Year(year=form.year.data))
            db.session.commit()  
        book.name = form.name.data
        book.img_url = 'http://lorempixel.com/250/400/'
        book.description = form.description.data
        book.year_id = Year.query.filter_by(year=form.year.data).first().id
        book.img_url = 'http://lorempixel.com/250/400/'
        db.session.add(book)
        flash('The book has been added.')
        return redirect(url_for('.add_book_admin'))
    return render_template('add_book_admin.html', form=form)


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