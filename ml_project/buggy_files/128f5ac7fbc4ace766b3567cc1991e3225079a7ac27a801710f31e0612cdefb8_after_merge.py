def _configuration_update_helper():
    reboot_required = False
    db_change = False
    to_save = request.form.to_dict()

    to_save['config_calibre_dir'] = re.sub('[[\\/]metadata\.db$', '', to_save['config_calibre_dir'], flags=re.IGNORECASE)
    db_change |= _config_string(to_save, "config_calibre_dir")

    # Google drive setup
    gdriveError = _configuration_gdrive_helper(to_save)

    reboot_required |= _config_int(to_save, "config_port")

    reboot_required |= _config_string(to_save, "config_keyfile")
    if config.config_keyfile and not os.path.isfile(config.config_keyfile):
        return _configuration_result(_('Keyfile Location is not Valid, Please Enter Correct Path'), gdriveError)

    reboot_required |= _config_string(to_save, "config_certfile")
    if config.config_certfile and not os.path.isfile(config.config_certfile):
        return _configuration_result(_('Certfile Location is not Valid, Please Enter Correct Path'), gdriveError)

    _config_checkbox_int(to_save, "config_uploading")
    _config_checkbox_int(to_save, "config_anonbrowse")
    _config_checkbox_int(to_save, "config_public_reg")
    reboot_required |= _config_checkbox_int(to_save, "config_kobo_sync")
    _config_checkbox_int(to_save, "config_kobo_proxy")

    _config_string(to_save, "config_upload_formats")
    constants.EXTENSIONS_UPLOAD = [x.lstrip().rstrip() for x in config.config_upload_formats.split(',')]

    _config_string(to_save, "config_calibre")
    _config_string(to_save, "config_converterpath")
    _config_string(to_save, "config_kepubifypath")

    reboot_required |= _config_int(to_save, "config_login_type")

    #LDAP configurator,
    if config.config_login_type == constants.LOGIN_LDAP:
        reboot_required |= _configuration_ldap_helper(to_save, gdriveError)

    # Remote login configuration
    _config_checkbox(to_save, "config_remote_login")
    if not config.config_remote_login:
        ub.session.query(ub.RemoteAuthToken).filter(ub.RemoteAuthToken.token_type==0).delete()

    # Goodreads configuration
    _config_checkbox(to_save, "config_use_goodreads")
    _config_string(to_save, "config_goodreads_api_key")
    _config_string(to_save, "config_goodreads_api_secret")
    if services.goodreads_support:
        services.goodreads_support.connect(config.config_goodreads_api_key,
                                           config.config_goodreads_api_secret,
                                           config.config_use_goodreads)

    _config_int(to_save, "config_updatechannel")

    # Reverse proxy login configuration
    _config_checkbox(to_save, "config_allow_reverse_proxy_header_login")
    _config_string(to_save, "config_reverse_proxy_login_header_name")

    # OAuth configuration
    if config.config_login_type == constants.LOGIN_OAUTH:
        _configuration_oauth_helper(to_save)

    reboot_required |= _configuration_logfile_helper(to_save, gdriveError)
    # Rarfile Content configuration
    _config_string(to_save, "config_rarfile_location")
    unrar_status = helper.check_unrar(config.config_rarfile_location)
    if unrar_status:
        return _configuration_result(unrar_status, gdriveError)

    try:
        metadata_db = os.path.join(config.config_calibre_dir, "metadata.db")
        if config.config_use_google_drive and is_gdrive_ready() and not os.path.exists(metadata_db):
            gdriveutils.downloadFile(None, "metadata.db", metadata_db)
            db_change = True
    except Exception as e:
        return _configuration_result('%s' % e, gdriveError)

    if db_change:
        if not db.setup_db(config):
            return _configuration_result(_('DB Location is not Valid, Please Enter Correct Path'), gdriveError)
        if not os.access(os.path.join(config.config_calibre_dir, "metadata.db"), os.W_OK):
            flash(_(u"DB is not writeable"), category="warning")

    config.save()
    flash(_(u"Calibre-Web configuration updated"), category="success")
    if reboot_required:
        web_server.stop(True)

    return _configuration_result(None, gdriveError)