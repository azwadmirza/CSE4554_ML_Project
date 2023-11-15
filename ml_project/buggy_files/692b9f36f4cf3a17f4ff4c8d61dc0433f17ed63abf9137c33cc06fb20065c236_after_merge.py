def configuration_helper(origin):
    reboot_required = False
    gdriveError=None
    db_change = False
    success = False
    filedata = None
    if gdriveutils.gdrive_support == False:
        gdriveError = _('Import of optional Google Drive requirements missing')
    else:
        if not os.path.isfile(os.path.join(config.get_main_dir,'client_secrets.json')):
            gdriveError = _('client_secrets.json is missing or not readable')
        else:
            with open(os.path.join(config.get_main_dir,'client_secrets.json'), 'r') as settings:
                filedata=json.load(settings)
            if not 'web' in filedata:
                gdriveError = _('client_secrets.json is not configured for web application')
    if request.method == "POST":
        to_save = request.form.to_dict()
        content = ub.session.query(ub.Settings).first()  # type: ub.Settings
        if "config_calibre_dir" in to_save:
            if content.config_calibre_dir != to_save["config_calibre_dir"]:
                content.config_calibre_dir = to_save["config_calibre_dir"]
                db_change = True
        # Google drive setup
        if not os.path.isfile(os.path.join(config.get_main_dir, 'settings.yaml')):
            content.config_use_google_drive = False
        if "config_use_google_drive" in to_save and not content.config_use_google_drive and not gdriveError:
            if filedata:
                if filedata['web']['redirect_uris'][0].endswith('/'):
                    filedata['web']['redirect_uris'][0] = filedata['web']['redirect_uris'][0][:-1]
                with open(os.path.join(config.get_main_dir,'settings.yaml'), 'w') as f:
                    yaml = "client_config_backend: settings\nclient_config_file: %(client_file)s\n" \
                           "client_config:\n" \
                           "  client_id: %(client_id)s\n  client_secret: %(client_secret)s\n" \
                           "  redirect_uri: %(redirect_uri)s\n\nsave_credentials: True\n" \
                           "save_credentials_backend: file\nsave_credentials_file: %(credential)s\n\n" \
                           "get_refresh_token: True\n\noauth_scope:\n" \
                           "  - https://www.googleapis.com/auth/drive\n"
                    f.write(yaml % {'client_file': os.path.join(config.get_main_dir,'client_secrets.json'),
                                    'client_id': filedata['web']['client_id'],
                                   'client_secret': filedata['web']['client_secret'],
                                   'redirect_uri': filedata['web']['redirect_uris'][0],
                                    'credential': os.path.join(config.get_main_dir,'gdrive_credentials')})
            else:
                flash(_(u'client_secrets.json is not configured for web application'), category="error")
                return render_title_template("config_edit.html", content=config, origin=origin,
                                             gdrive=gdriveutils.gdrive_support, gdriveError=gdriveError,
                                             goodreads=goodreads_support, title=_(u"Basic Configuration"),
                                             page="config")
        # always show google drive settings, but in case of error deny support
        if "config_use_google_drive" in to_save and not gdriveError:
            content.config_use_google_drive = "config_use_google_drive" in to_save
        else:
            content.config_use_google_drive = 0
        if "config_google_drive_folder" in to_save:
            if content.config_google_drive_folder != to_save["config_google_drive_folder"]:
                content.config_google_drive_folder = to_save["config_google_drive_folder"]
                gdriveutils.deleteDatabaseOnChange()

        if "config_port" in to_save:
            if content.config_port != int(to_save["config_port"]):
                content.config_port = int(to_save["config_port"])
                reboot_required = True
        if "config_keyfile" in to_save:
            if content.config_keyfile != to_save["config_keyfile"]:
                if os.path.isfile(to_save["config_keyfile"]) or to_save["config_keyfile"] is u"":
                    content.config_keyfile = to_save["config_keyfile"]
                    reboot_required = True
                else:
                    ub.session.commit()
                    flash(_(u'Keyfile location is not valid, please enter correct path'), category="error")
                    return render_title_template("config_edit.html", content=config, origin=origin,
                                                 gdrive=gdriveutils.gdrive_support, gdriveError=gdriveError,
                                                 goodreads=goodreads_support, title=_(u"Basic Configuration"),
                                                 page="config")
        if "config_certfile" in to_save:
            if content.config_certfile != to_save["config_certfile"]:
                if os.path.isfile(to_save["config_certfile"]) or to_save["config_certfile"] is u"":
                    content.config_certfile = to_save["config_certfile"]
                    reboot_required = True
                else:
                    ub.session.commit()
                    flash(_(u'Certfile location is not valid, please enter correct path'), category="error")
                    return render_title_template("config_edit.html", content=config, origin=origin,
                                                 gdrive=gdriveutils.gdrive_support, gdriveError=gdriveError,
                                                 goodreads=goodreads_support, title=_(u"Basic Configuration"),
                                                 page="config")
        content.config_uploading = 0
        content.config_anonbrowse = 0
        content.config_public_reg = 0
        if "config_uploading" in to_save and to_save["config_uploading"] == "on":
            content.config_uploading = 1
        if "config_anonbrowse" in to_save and to_save["config_anonbrowse"] == "on":
            content.config_anonbrowse = 1
        if "config_public_reg" in to_save and to_save["config_public_reg"] == "on":
            content.config_public_reg = 1

        if "config_converterpath" in to_save:
            content.config_converterpath = to_save["config_converterpath"].strip()
        if "config_calibre" in to_save:
            content.config_calibre = to_save["config_calibre"].strip()
        if "config_ebookconverter" in to_save:
            content.config_ebookconverter = int(to_save["config_ebookconverter"])

        # Remote login configuration
        content.config_remote_login = ("config_remote_login" in to_save and to_save["config_remote_login"] == "on")
        if not content.config_remote_login:
            ub.session.query(ub.RemoteAuthToken).delete()

        # Goodreads configuration
        content.config_use_goodreads = ("config_use_goodreads" in to_save and to_save["config_use_goodreads"] == "on")
        if "config_goodreads_api_key" in to_save:
            content.config_goodreads_api_key = to_save["config_goodreads_api_key"]
        if "config_goodreads_api_secret" in to_save:
            content.config_goodreads_api_secret = to_save["config_goodreads_api_secret"]
        if "config_updater" in to_save:
            content.config_updatechannel = int(to_save["config_updater"])
        if "config_log_level" in to_save:
            content.config_log_level = int(to_save["config_log_level"])
        if content.config_logfile != to_save["config_logfile"]:
            # check valid path, only path or file
            if os.path.dirname(to_save["config_logfile"]):
                if os.path.exists(os.path.dirname(to_save["config_logfile"])) and \
                        os.path.basename(to_save["config_logfile"]) and not os.path.isdir(to_save["config_logfile"]):
                    content.config_logfile = to_save["config_logfile"]
                else:
                    ub.session.commit()
                    flash(_(u'Logfile location is not valid, please enter correct path'), category="error")
                    return render_title_template("config_edit.html", content=config, origin=origin,
                                                 gdrive=gdriveutils.gdrive_support, gdriveError=gdriveError,
                                                 goodreads=goodreads_support, title=_(u"Basic Configuration"),
                                                 page="config")
            else:
                content.config_logfile = to_save["config_logfile"]
            reboot_required = True

        # Rarfile Content configuration
        if "config_rarfile_location" in to_save and to_save['config_rarfile_location'] is not u"":
            check = helper.check_unrar(to_save["config_rarfile_location"].strip())
            if not check[0] :
                content.config_rarfile_location = to_save["config_rarfile_location"].strip()
            else:
                flash(check[1], category="error")
                return render_title_template("config_edit.html", content=config, origin=origin,
                                             gdrive=gdriveutils.gdrive_support, goodreads=goodreads_support,
                                             rarfile_support=rar_support, title=_(u"Basic Configuration"))
        try:
            if content.config_use_google_drive and is_gdrive_ready() and not \
                    os.path.exists(os.path.join(content.config_calibre_dir, "metadata.db")):
                gdriveutils.downloadFile(None, "metadata.db", config.config_calibre_dir + "/metadata.db")
            if db_change:
                if config.db_configured:
                    db.session.close()
                    db.engine.dispose()
            ub.session.commit()
            flash(_(u"Calibre-Web configuration updated"), category="success")
            config.loadSettings()
            app.logger.setLevel(config.config_log_level)
            logging.getLogger("book_formats").setLevel(config.config_log_level)
        except Exception as e:
            flash(e, category="error")
            return render_title_template("config_edit.html", content=config, origin=origin,
                                         gdrive=gdriveutils.gdrive_support, gdriveError=gdriveError,
                                         goodreads=goodreads_support, rarfile_support=rar_support,
                                         title=_(u"Basic Configuration"), page="config")
        if db_change:
            reload(db)
            if not db.setup_db():
                flash(_(u'DB location is not valid, please enter correct path'), category="error")
                return render_title_template("config_edit.html", content=config, origin=origin,
                                             gdrive=gdriveutils.gdrive_support,gdriveError=gdriveError,
                                             goodreads=goodreads_support, rarfile_support=rar_support,
                                             title=_(u"Basic Configuration"), page="config")
        if reboot_required:
            # stop Server
            server.Server.setRestartTyp(True)
            server.Server.stopServer()
            app.logger.info('Reboot required, restarting')
        if origin:
            success = True
    if is_gdrive_ready() and gdriveutils.gdrive_support == True: # and config.config_use_google_drive == True:
        gdrivefolders=gdriveutils.listRootFolders()
    else:
        gdrivefolders=list()
    return render_title_template("config_edit.html", origin=origin, success=success, content=config,
                                 show_authenticate_google_drive=not is_gdrive_ready(),
                                 gdrive=gdriveutils.gdrive_support, gdriveError=gdriveError,
                                 gdrivefolders=gdrivefolders, rarfile_support=rar_support,
                                 goodreads=goodreads_support, title=_(u"Basic Configuration"), page="config")