import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'temporarySecretKey'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'vb2109@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '741963789123q'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Elibrary]'
    FLASKY_MAIL_SENDER = 'Elibrary <some@example.com>'
    FLASKY_ADMIN = os.environ.get('ELIBRARY_ADMIN')
    FLASKY_BOOKS_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
