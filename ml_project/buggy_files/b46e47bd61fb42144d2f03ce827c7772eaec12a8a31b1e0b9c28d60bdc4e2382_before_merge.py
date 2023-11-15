def view_configuration():
    reboot_required = False
    if request.method == "POST":
        to_save = request.form.to_dict()
        content = ub.session.query(ub.Settings).first()
        if "config_calibre_web_title" in to_save:
            content.config_calibre_web_title = to_save["config_calibre_web_title"]
        if "config_columns_to_ignore" in to_save:
            content.config_columns_to_ignore = to_save["config_columns_to_ignore"]
        if "config_read_column" in to_save:
            content.config_read_column = int(to_save["config_read_column"])
        if "config_title_regex" in to_save:
            if content.config_title_regex != to_save["config_title_regex"]:
                content.config_title_regex = to_save["config_title_regex"]
                reboot_required = True
        if "config_random_books" in to_save:
            content.config_random_books = int(to_save["config_random_books"])
        if "config_books_per_page" in to_save:
            content.config_books_per_page = int(to_save["config_books_per_page"])
        # Mature Content configuration
        if "config_mature_content_tags" in to_save:
            content.config_mature_content_tags = to_save["config_mature_content_tags"].strip()

        # Default user configuration
        content.config_default_role = 0
        if "admin_role" in to_save:
            content.config_default_role = content.config_default_role + ub.ROLE_ADMIN
        if "download_role" in to_save:
            content.config_default_role = content.config_default_role + ub.ROLE_DOWNLOAD
        if "upload_role" in to_save:
            content.config_default_role = content.config_default_role + ub.ROLE_UPLOAD
        if "edit_role" in to_save:
            content.config_default_role = content.config_default_role + ub.ROLE_EDIT
        if "delete_role" in to_save:
            content.config_default_role = content.config_default_role + ub.ROLE_DELETE_BOOKS
        if "passwd_role" in to_save:
            content.config_default_role = content.config_default_role + ub.ROLE_PASSWD
        if "passwd_role" in to_save:
            content.config_default_role = content.config_default_role + ub.ROLE_EDIT_SHELFS
        content.config_default_show = 0
        if "show_detail_random" in to_save:
            content.config_default_show = content.config_default_show + ub.DETAIL_RANDOM
        if "show_language" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_LANGUAGE
        if "show_series" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_SERIES
        if "show_category" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_CATEGORY
        if "show_hot" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_HOT
        if "show_random" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_RANDOM
        if "show_author" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_AUTHOR
        if "show_publisher" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_PUBLISHER
        if "show_best_rated" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_BEST_RATED
        if "show_read_and_unread" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_READ_AND_UNREAD
        if "show_recent" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_RECENT
        if "show_sorted" in to_save:
            content.config_default_show = content.config_default_show + ub.SIDEBAR_SORTED
        if "show_mature_content" in to_save:
            content.config_default_show = content.config_default_show + ub.MATURE_CONTENT
        ub.session.commit()
        flash(_(u"Calibre-Web configuration updated"), category="success")
        config.loadSettings()
        if reboot_required:
            # db.engine.dispose() # ToDo verify correct
            # ub.session.close()
            # ub.engine.dispose()
            # stop Server
            server.Server.setRestartTyp(True)
            server.Server.stopServer()
            app.logger.info('Reboot required, restarting')
    readColumn = db.session.query(db.Custom_Columns)\
            .filter(db.and_(db.Custom_Columns.datatype == 'bool',db.Custom_Columns.mark_for_delete == 0)).all()
    return render_title_template("config_view_edit.html", content=config, readColumns=readColumn,
                                 title=_(u"UI Configuration"), page="uiconfig")