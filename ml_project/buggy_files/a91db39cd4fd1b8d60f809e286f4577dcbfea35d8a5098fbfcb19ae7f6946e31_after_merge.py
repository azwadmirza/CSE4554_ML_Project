def upload():
    if not config.config_uploading:
        abort(404)
    if request.method == 'POST' and 'btn-upload' in request.files:
        for requested_file in request.files.getlist("btn-upload"):
            # create the function for sorting...
            db.session.connection().connection.connection.create_function("title_sort", 1, db.title_sort)
            db.session.connection().connection.connection.create_function('uuid4', 0, lambda: str(uuid4()))

            # check if file extension is correct
            if '.' in requested_file.filename:
                file_ext = requested_file.filename.rsplit('.', 1)[-1].lower()
                if file_ext not in EXTENSIONS_UPLOAD:
                    return Response(_("File extension '%(ext)s' is not allowed to be uploaded to this server",
                          ext=file_ext)), 422
            else:
                return Response(_('File to be uploaded must have an extension')), 422

            # extract metadata from file
            meta = uploader.upload(requested_file)
            title = meta.title
            authr = meta.author
            tags = meta.tags
            series = meta.series
            series_index = meta.series_id
            title_dir = helper.get_valid_filename(title)
            author_dir = helper.get_valid_filename(authr)
            filepath = os.path.join(config.config_calibre_dir, author_dir, title_dir)
            saved_filename = os.path.join(filepath, title_dir + meta.extension.lower())

            # check if file path exists, otherwise create it, copy file to calibre path and delete temp file
            if not os.path.exists(filepath):
                try:
                    os.makedirs(filepath)
                except OSError:
                    return Response(_(u"Failed to create path %(path)s (Permission denied).", path=filepath)), 422
            try:
                copyfile(meta.file_path, saved_filename)
            except OSError:
                return Response(_(u"Failed to store file %(file)s (Permission denied).", file=saved_filename)), 422

            try:
                os.unlink(meta.file_path)
            except OSError:
                flash(_(u"Failed to delete file %(file)s (Permission denied).", file= meta.file_path),
                      category="warning")

            if meta.cover is None:
                has_cover = 0
                copyfile(os.path.join(config.get_main_dir, "cps/static/generic_cover.jpg"),
                         os.path.join(filepath, "cover.jpg"))
            else:
                has_cover = 1
                move(meta.cover, os.path.join(filepath, "cover.jpg"))

            # handle authors
            is_author = db.session.query(db.Authors).filter(db.Authors.name == authr).first()
            if is_author:
                db_author = is_author
            else:
                db_author = db.Authors(authr, helper.get_sorted_author(authr), "")
                db.session.add(db_author)

            # handle series
            db_series = None
            is_series = db.session.query(db.Series).filter(db.Series.name == series).first()
            if is_series:
                db_series = is_series
            elif series != '':
                db_series = db.Series(series, "")
                db.session.add(db_series)

            # add language actually one value in list
            input_language = meta.languages
            db_language = None
            if input_language != "":
                input_language = isoLanguages.get(name=input_language).part3
                hasLanguage = db.session.query(db.Languages).filter(db.Languages.lang_code == input_language).first()
                if hasLanguage:
                    db_language = hasLanguage
                else:
                    db_language = db.Languages(input_language)
                    db.session.add(db_language)

            # combine path and normalize path from windows systems
            path = os.path.join(author_dir, title_dir).replace('\\', '/')
            db_book = db.Books(title, "", db_author.sort, datetime.datetime.now(), datetime.datetime(101, 1, 1),
                            series_index, datetime.datetime.now(), path, has_cover, db_author, [], db_language)
            db_book.authors.append(db_author)
            if db_series:
                db_book.series.append(db_series)
            if db_language is not None:
                db_book.languages.append(db_language)
            file_size = os.path.getsize(saved_filename)
            db_data = db.Data(db_book, meta.extension.upper()[1:], file_size, title_dir)

            # handle tags
            input_tags = tags.split(',')
            input_tags = list(map(lambda it: it.strip(), input_tags))
            if input_tags[0] !="":
                modify_database_object(input_tags, db_book.tags, db.Tags, db.session, 'tags')

            # flush content, get db_book.id available
            db_book.data.append(db_data)
            db.session.add(db_book)
            db.session.flush()

            # add comment
            book_id = db_book.id
            upload_comment = Markup(meta.description).unescape()
            if upload_comment != "":
                db.session.add(db.Comments(upload_comment, book_id))

            # save data to database, reread data
            db.session.commit()
            db.session.connection().connection.connection.create_function("title_sort", 1, db.title_sort)
            book = db.session.query(db.Books).filter(db.Books.id == book_id).filter(common_filters()).first()

            # upload book to gdrive if nesseccary and add "(bookid)" to folder name
            if config.config_use_google_drive:
                gdriveutils.updateGdriveCalibreFromLocal()
            error = helper.update_dir_stucture(book.id, config.config_calibre_dir)
            db.session.commit()
            if config.config_use_google_drive:
                gdriveutils.updateGdriveCalibreFromLocal()
            if error:
                flash(error, category="error")
            uploadText=_(u"File %(title)s", title=book.title)
            helper.global_WorkerThread.add_upload(current_user.nickname,
                "<a href=\"" + url_for('show_book', book_id=book.id) + "\">" + uploadText + "</a>")

            # create data for displaying display Full language name instead of iso639.part3language
            if db_language is not None:
                book.languages[0].language_name = _(meta.languages)
            author_names = []
            for author in db_book.authors:
                author_names.append(author.name)
            if len(request.files.getlist("btn-upload")) < 2:
                if current_user.role_edit() or current_user.role_admin():
                    resp = {"location": url_for('edit_book', book_id=db_book.id)}
                    return Response(json.dumps(resp), mimetype='application/json')
                else:
                    resp = {"location": url_for('show_book', book_id=db_book.id)}
                    return Response(json.dumps(resp), mimetype='application/json')
    return Response(json.dumps({"location": url_for("index")}), mimetype='application/json')