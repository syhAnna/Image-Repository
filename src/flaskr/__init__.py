# -*- coding: utf-8 -*-
# author: zyk
import os
import logging
logging.basicConfig(filename='catEatPad_test.log', level=logging.INFO)
from flask import Flask


UPLOAD_FOLDER = "/static/pic/upload_folder"
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # mysql = MySQL()
    app.config.from_mapping(    # sets some default configuration that the app will use
         SECRET_KEY='dev',
    )
    app.config['UPLOAD_FOLDER'] = "./flaskr" + UPLOAD_FOLDER

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    print("__init__.py is going to init_app")
    db.init_app(app)

    # XX/auth
    from . import auth
    app.register_blueprint(auth.bp)

    # XX/user
    from . import user
    app.register_blueprint(user.bp)

    # XX/blog
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app