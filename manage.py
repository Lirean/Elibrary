#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Book, Author, Year
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
import flask.ext.whooshalchemy as whooshalchemy

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

whooshalchemy.whoosh_index(app, Book)
whooshalchemy.whoosh_index(app, Author)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Book=Book,
    			Author=Author, Year=Year)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
