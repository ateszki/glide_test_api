import os

from flask import Flask, make_response, jsonify


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        from config import Config
        app.config.from_object(Config())
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)


    from . import api
    app.register_blueprint(api.bp)
    app.add_url_rule('/employees', endpoint='employees')
    app.add_url_rule('/departments', endpoint='departments')
    app.add_url_rule('/offices', endpoint='offices')

    return app