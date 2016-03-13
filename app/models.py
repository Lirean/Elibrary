from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db, login_manager
import flask.ext.whooshalchemy as whooshalchemy


class Permission:
    COMMENT = 0x01
    ADD_BOOKS = 0x02
    MODERATE_BOOKS = 0x04
    MODERATE_COMMENTS = 0x08
    MODERATE_LIBRARY = 0x10
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMENT |
                     Permission.ADD_BOOKS, True),
            'Moderator': (Permission.COMMENT |
                          Permission.ADD_BOOKS |
                          Permission.MODERATE_COMMENTS |
                          Permission.MODERATE_BOOKS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


user_book_reg = db.Table('user_book_reg',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
                         db.PrimaryKeyConstraint('user_id', 'book_id') )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    books = db.relationship('Book',
                              secondary=user_book_reg,
                              backref=db.backref('users', lazy='dynamic'),
                              lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ELIBRARY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=4800):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=4800):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=4800):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


book_author_reg = db.Table('book_author_reg',
                         db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
                         db.Column('author_id', db.Integer, db.ForeignKey('authors.id')),
                         db.PrimaryKeyConstraint('book_id', 'author_id') )


class Book(db.Model):
    __tablename__ = 'books'
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(2048))
    authors = db.relationship('Author', backref='role', lazy='dynamic')
    year_id = db.Column(db.Integer, db.ForeignKey('years.id'))
    img_url = db.Column(db.String(255))
    authors = db.relationship('Author',
                              secondary=book_author_reg,
                              backref=db.backref('books', lazy='dynamic'),
                              lazy='dynamic')

    @staticmethod
    def generate_fake(count=500):
        from random import seed, randint
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        seed()
        author_count = Author.query.count()
        year_count = Year.query.count()
        for i in range(count):
            b = Book()
            for j in range(randint(1,3)):
                a = Author.query.offset(randint(0, author_count - 1)).first()
                b.authors.append(a)
            b.name = forgery_py.lorem_ipsum.word()
            b.img_url = 'http://lorempixel.com/250/400/'+'?%s' % i
            b.description = forgery_py.lorem_ipsum.sentences(randint(2, 10))
            b.year_id = randint(0, year_count - 1)
            db.session.add(b)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '%r' % self.name

class Author(db.Model):
    __tablename__ = 'authors'
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    @staticmethod
    def generate_fake(count=300):
        from random import seed
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        seed()
        for i in range(count):
            a = Author(name = forgery_py.name.full_name())
            db.session.add(a)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '%r' % self.name

class Year(db.Model):
    __tablename__ = 'years'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True)
    books = db.relationship('Book', backref='year', lazy='dynamic')

    @staticmethod
    def generate_fake(count=300):
        from random import seed
        from sqlalchemy.exc import IntegrityError        
        import forgery_py

        seed()
        for i in range(count):
            y = Year(year = forgery_py.forgery.date.year(past=True))
            db.session.add(y)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '%r' % self.year