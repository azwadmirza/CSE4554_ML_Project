def edit_user(user_id):
    content = ub.session.query(ub.User).filter(ub.User.id == int(user_id)).first()  # type: ub.User
    downloads = list()
    languages = speaking_language()
    translations = babel.list_translations() + [LC('en')]
    for book in content.downloads:
        downloadbook = db.session.query(db.Books).filter(db.Books.id == book.book_id).first()
        if downloadbook:
            downloads.append(downloadbook)
        else:
            ub.delete_download(book.book_id)
            # ub.session.query(ub.Downloads).filter(book.book_id == ub.Downloads.book_id).delete()
            # ub.session.commit()
    if request.method == "POST":
        to_save = request.form.to_dict()
        if "delete" in to_save:
            ub.session.query(ub.User).filter(ub.User.id == content.id).delete()
            ub.session.commit()
            flash(_(u"User '%(nick)s' deleted", nick=content.nickname), category="success")
            return redirect(url_for('admin'))
        else:
            if "password" in to_save and to_save["password"]:
                content.password = generate_password_hash(to_save["password"])

            if "admin_role" in to_save and not content.role_admin():
                content.role = content.role + ub.ROLE_ADMIN
            elif "admin_role" not in to_save and content.role_admin():
                content.role = content.role - ub.ROLE_ADMIN

            if "download_role" in to_save and not content.role_download():
                content.role = content.role + ub.ROLE_DOWNLOAD
            elif "download_role" not in to_save and content.role_download():
                content.role = content.role - ub.ROLE_DOWNLOAD

            if "upload_role" in to_save and not content.role_upload():
                content.role = content.role + ub.ROLE_UPLOAD
            elif "upload_role" not in to_save and content.role_upload():
                content.role = content.role - ub.ROLE_UPLOAD

            if "edit_role" in to_save and not content.role_edit():
                content.role = content.role + ub.ROLE_EDIT
            elif "edit_role" not in to_save and content.role_edit():
                content.role = content.role - ub.ROLE_EDIT

            if "delete_role" in to_save and not content.role_delete_books():
                content.role = content.role + ub.ROLE_DELETE_BOOKS
            elif "delete_role" not in to_save and content.role_delete_books():
                content.role = content.role - ub.ROLE_DELETE_BOOKS

            if "passwd_role" in to_save and not content.role_passwd():
                content.role = content.role + ub.ROLE_PASSWD
            elif "passwd_role" not in to_save and content.role_passwd():
                content.role = content.role - ub.ROLE_PASSWD

            if "edit_shelf_role" in to_save and not content.role_edit_shelfs():
                content.role = content.role + ub.ROLE_EDIT_SHELFS
            elif "edit_shelf_role" not in to_save and content.role_edit_shelfs():
                content.role = content.role - ub.ROLE_EDIT_SHELFS

            if "show_random" in to_save and not content.show_random_books():
                content.sidebar_view += ub.SIDEBAR_RANDOM
            elif "show_random" not in to_save and content.show_random_books():
                content.sidebar_view -= ub.SIDEBAR_RANDOM

            if "show_language" in to_save and not content.show_language():
                content.sidebar_view += ub.SIDEBAR_LANGUAGE
            elif "show_language" not in to_save and content.show_language():
                content.sidebar_view -= ub.SIDEBAR_LANGUAGE

            if "show_series" in to_save and not content.show_series():
                content.sidebar_view += ub.SIDEBAR_SERIES
            elif "show_series" not in to_save and content.show_series():
                content.sidebar_view -= ub.SIDEBAR_SERIES

            if "show_category" in to_save and not content.show_category():
                content.sidebar_view += ub.SIDEBAR_CATEGORY
            elif "show_category" not in to_save and content.show_category():
                content.sidebar_view -= ub.SIDEBAR_CATEGORY

            if "show_recent" in to_save and not content.show_recent():
                content.sidebar_view += ub.SIDEBAR_RECENT
            elif "show_recent" not in to_save and content.show_recent():
                content.sidebar_view -= ub.SIDEBAR_RECENT

            if "show_sorted" in to_save and not content.show_sorted():
                content.sidebar_view += ub.SIDEBAR_SORTED
            elif "show_sorted" not in to_save and content.show_sorted():
                content.sidebar_view -= ub.SIDEBAR_SORTED

            if "show_publisher" in to_save and not content.show_publisher():
                content.sidebar_view += ub.SIDEBAR_PUBLISHER
            elif "show_publisher" not in to_save and content.show_publisher():
                content.sidebar_view -= ub.SIDEBAR_PUBLISHER

            if "show_hot" in to_save and not content.show_hot_books():
                content.sidebar_view += ub.SIDEBAR_HOT
            elif "show_hot" not in to_save and content.show_hot_books():
                content.sidebar_view -= ub.SIDEBAR_HOT

            if "show_best_rated" in to_save and not content.show_best_rated_books():
                content.sidebar_view += ub.SIDEBAR_BEST_RATED
            elif "show_best_rated" not in to_save and content.show_best_rated_books():
                content.sidebar_view -= ub.SIDEBAR_BEST_RATED

            if "show_read_and_unread" in to_save and not content.show_read_and_unread():
                content.sidebar_view += ub.SIDEBAR_READ_AND_UNREAD
            elif "show_read_and_unread" not in to_save and content.show_read_and_unread():
                content.sidebar_view -= ub.SIDEBAR_READ_AND_UNREAD

            if "show_author" in to_save and not content.show_author():
                content.sidebar_view += ub.SIDEBAR_AUTHOR
            elif "show_author" not in to_save and content.show_author():
                content.sidebar_view -= ub.SIDEBAR_AUTHOR

            if "show_detail_random" in to_save and not content.show_detail_random():
                content.sidebar_view += ub.DETAIL_RANDOM
            elif "show_detail_random" not in to_save and content.show_detail_random():
                content.sidebar_view -= ub.DETAIL_RANDOM

            content.mature_content = "show_mature_content" in to_save

            if "default_language" in to_save:
                content.default_language = to_save["default_language"]
            if "locale" in to_save and to_save["locale"]:
                content.locale = to_save["locale"]
            if to_save["email"] and to_save["email"] != content.email:
                content.email = to_save["email"]
            if "kindle_mail" in to_save and to_save["kindle_mail"] != content.kindle_mail:
                content.kindle_mail = to_save["kindle_mail"]
        try:
            ub.session.commit()
            flash(_(u"User '%(nick)s' updated", nick=content.nickname), category="success")
        except IntegrityError:
            ub.session.rollback()
            flash(_(u"An unknown error occured."), category="error")
    return render_title_template("user_edit.html", translations=translations, languages=languages, new_user=0,
                                content=content, downloads=downloads, title=_(u"Edit User %(nick)s",
                                nick=content.nickname), page="edituser")