def create_app():
    global app_created
    if not app_created:
        BlueprintsManager.register(app)
    Migrate(app, db)

    app.config.from_object(env('APP_CONFIG', default='config.ProductionConfig'))
    db.init_app(app)
    _manager = Manager(app)
    _manager.add_command('db', MigrateCommand)

    if app.config['CACHING']:
        cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    else:
        cache.init_app(app, config={'CACHE_TYPE': 'null'})

    stripe.api_key = 'SomeStripeKey'
    app.secret_key = 'super secret key'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    # set up jwt
    app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=24 * 60 * 60)
    app.config['JWT_AUTH_URL_RULE'] = '/auth/session'
    _jwt = JWT(app, jwt_authenticate, jwt_identity)

    # setup celery
    app.config['CELERY_BROKER_URL'] = app.config['REDIS_URL']
    app.config['CELERY_RESULT_BACKEND'] = app.config['CELERY_BROKER_URL']

    CORS(app, resources={r"/*": {"origins": "*"}})
    AuthManager.init_login(app)

    if app.config['TESTING'] and app.config['PROFILE']:
        # Profiling
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    # development api
    with app.app_context():
        from app.api.admin_statistics_api.events import event_statistics
        from app.api.auth import auth_routes
        from app.api.attendees import attendee_misc_routes
        from app.api.bootstrap import api_v1
        from app.api.celery_tasks import celery_routes
        from app.api.event_copy import event_copy
        from app.api.exports import export_routes
        from app.api.imports import import_routes
        from app.api.uploads import upload_routes
        from app.api.users import user_misc_routes
        from app.api.orders import order_misc_routes
        from app.api.role_invites import role_invites_misc_routes
        from app.api.auth import ticket_blueprint, authorised_blueprint
        from app.api.admin_translations import admin_blueprint
        from app.api.orders import alipay_blueprint

        app.register_blueprint(api_v1)
        app.register_blueprint(event_copy)
        app.register_blueprint(upload_routes)
        app.register_blueprint(export_routes)
        app.register_blueprint(import_routes)
        app.register_blueprint(celery_routes)
        app.register_blueprint(auth_routes)
        app.register_blueprint(event_statistics)
        app.register_blueprint(user_misc_routes)
        app.register_blueprint(attendee_misc_routes)
        app.register_blueprint(order_misc_routes)
        app.register_blueprint(role_invites_misc_routes)
        app.register_blueprint(ticket_blueprint)
        app.register_blueprint(authorised_blueprint)
        app.register_blueprint(admin_blueprint)
        app.register_blueprint(alipay_blueprint)

    sa.orm.configure_mappers()

    if app.config['SERVE_STATIC']:
        app.add_url_rule('/static/<path:filename>',
                         endpoint='static',
                         view_func=app.send_static_file)

    # sentry
    if not app_created and 'SENTRY_DSN' in app.config:
        sentry_sdk.init(app.config['SENTRY_DSN'], integrations=[FlaskIntegration()])

    # redis
    redis_store.init_app(app)

    # elasticsearch
    if app.config['ENABLE_ELASTICSEARCH']:
        client.init_app(app)
        connections.add_connection('default', client.elasticsearch)
        with app.app_context():
            try:
                cron_rebuild_events_elasticsearch.delay()
            except Exception:
                pass

    app_created = True
    return app, _manager, db, _jwt