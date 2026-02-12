import os

from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        return render_template("dashboard/welcome.html")

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import upload

    app.register_blueprint(upload.bp)

    from . import process_dict

    app.register_blueprint(process_dict.bp)

    from . import dashboard

    app.register_blueprint(dashboard.bp)

    from . import flashcards

    app.register_blueprint(flashcards.bp)

    from . import profile

    app.register_blueprint(profile.bp)

    from . import reset

    app.register_blueprint(reset.bp)
    reset.init_app(app)

    from . import landing

    app.register_blueprint(landing.bp)

    return app
