def update_view_configuration():
    reboot_required = False
    to_save = request.form.to_dict()

    _config_string = lambda x: config.set_from_dictionary(to_save, x, lambda y: y.strip() if y else y)
    _config_int = lambda x: config.set_from_dictionary(to_save, x, int)

    _config_string("config_calibre_web_title")
    _config_string("config_columns_to_ignore")
    # _config_string("config_mature_content_tags")
    reboot_required |= _config_string("config_title_regex")

    _config_int("config_read_column")
    _config_int("config_theme")
    _config_int("config_random_books")
    _config_int("config_books_per_page")
    _config_int("config_authors_max")
    _config_int("config_restricted_column")

    config.config_default_role = constants.selected_roles(to_save)
    config.config_default_role &= ~constants.ROLE_ANONYMOUS

    config.config_default_show = sum(int(k[5:]) for k in to_save if k.startswith('show_'))
    if "Show_detail_random" in to_save:
        config.config_default_show |= constants.DETAIL_RANDOM

    config.save()
    flash(_(u"Calibre-Web configuration updated"), category="success")
    before_request()
    if reboot_required:
        db.dispose()
        ub.dispose()
        web_server.stop(True)

    return view_configuration()