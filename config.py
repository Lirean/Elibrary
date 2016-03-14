import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'temporarySecretKey'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ELIBRARY_MAIL_SUBJECT_PREFIX = '[Elibrary]'
    ELIBRARY_MAIL_SENDER = 'Elibrary <some@example.com>'
    ELIBRARY_ADMIN = os.environ.get('ELIBRARY_ADMIN')
    ELIBRARY_BOOKS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 50

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    WHOOSH_BASE = SQLALCHEMY_DATABASE_URI

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WHOOSH_BASE = SQLALCHEMY_DATABASE_URI


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    WHOOSH_BASE = SQLALCHEMY_DATABASE_URI


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
