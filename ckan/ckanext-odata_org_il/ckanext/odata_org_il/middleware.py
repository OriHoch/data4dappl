from ckan.config.environment import load_environment
from ckan.config.middleware import AskAppDispatcherMiddleware
from .flask_app import make_flask_stack
from .pylons_app import make_pylons_stack


def make_app(conf, full_stack=True, static_files=True, **app_conf):
    '''
    Initialise both the pylons and flask apps, and wrap them in dispatcher
    middleware.
    '''
    load_environment(conf, app_conf)

    pylons_app = make_pylons_stack(conf, full_stack, static_files,
                                   **app_conf)
    flask_app = make_flask_stack(conf, **app_conf)

    app = AskAppDispatcherMiddleware({'pylons_app': pylons_app,
                                      'flask_app': flask_app})

    return app
