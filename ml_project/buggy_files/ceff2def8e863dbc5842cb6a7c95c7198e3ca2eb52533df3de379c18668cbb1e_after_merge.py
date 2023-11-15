def create_app(
    configuration=None, instance_path="/etc/ihatemoney", instance_relative_config=True
):
    app = Flask(
        __name__,
        instance_path=instance_path,
        instance_relative_config=instance_relative_config,
    )

    # If a configuration object is passed, use it. Otherwise try to find one.
    load_configuration(app, configuration)
    app.wsgi_app = PrefixedWSGI(app)

    # Get client's real IP
    # Note(0livd): When running in a non-proxy setup, is vulnerable to requests
    # with a forged X-FORWARDED-FOR header
    app.wsgi_app = ProxyFix(app.wsgi_app)

    validate_configuration(app)
    app.register_blueprint(web_interface)
    app.register_blueprint(apiv1)
    app.register_error_handler(404, page_not_found)

    # Configure the a, root="main"pplication
    setup_database(app)

    # Setup Currency Cache
    CurrencyConverter()

    mail = Mail()
    mail.init_app(app)
    app.mail = mail

    # Jinja filters
    app.jinja_env.globals["static_include"] = static_include
    app.jinja_env.globals["locale_from_iso"] = locale_from_iso
    app.jinja_env.filters["minimal_round"] = minimal_round

    # Translations
    babel = Babel(app)

    # Undocumented currencyformat filter from flask_babel is forwarding to Babel format_currency
    # We overwrite it to remove the currency sign ¤ when there is no currency
    def currencyformat_nc(number, currency, *args, **kwargs):
        """
        Same as flask_babel.Babel.currencyformat, but without the "no currency ¤" sign
        when there is no currency.
        """
        return format_currency(
            number,
            currency if currency != CurrencyConverter.no_currency else "",
            *args,
            **kwargs
        ).strip()

    app.jinja_env.filters["currencyformat_nc"] = currencyformat_nc

    @babel.localeselector
    def get_locale():
        # get the lang from the session if defined, fallback on the browser "accept
        # languages" header.
        lang = session.get(
            "lang",
            request.accept_languages.best_match(app.config["SUPPORTED_LANGUAGES"]),
        )
        setattr(g, "lang", lang)
        return lang

    return app