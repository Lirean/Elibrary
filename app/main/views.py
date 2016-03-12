from flask import render_template
from .. import db
from . import main


@main.route('/')
def index():
    return render_template('index.html')