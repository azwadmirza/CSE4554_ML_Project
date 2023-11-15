def before_request():
    g.user = current_user
    g.allow_registration = config.config_public_reg
    g.allow_upload = config.config_uploading
    g.current_theme = config.config_theme
    g.config_authors_max = config.config_authors_max
    g.public_shelfes = ub.session.query(ub.Shelf).filter(ub.Shelf.is_public == 1).order_by(ub.Shelf.name).all()
    if not config.db_configured and request.endpoint not in ('basic_configuration', 'login') and '/static/' not in request.path:
        return redirect(url_for('basic_configuration'))