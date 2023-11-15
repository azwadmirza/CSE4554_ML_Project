def upload_single_file(request, book, book_id):
    # Check and handle Uploaded file
    if 'btn-upload-format' in request.files:
        requested_file = request.files['btn-upload-format']
        # check for empty request
        if requested_file.filename != '':
            if '.' in requested_file.filename:
                file_ext = requested_file.filename.rsplit('.', 1)[-1].lower()
                if file_ext not in EXTENSIONS_UPLOAD:
                    flash(_("File extension '%(ext)s' is not allowed to be uploaded to this server", ext=file_ext),
                          category="error")
                    return redirect(url_for('show_book', book_id=book.id))
            else:
                flash(_('File to be uploaded must have an extension'), category="error")
                return redirect(url_for('show_book', book_id=book.id))

            file_name = book.path.rsplit('/', 1)[-1]
            filepath = os.path.normpath(os.path.join(config.config_calibre_dir, book.path))
            saved_filename = os.path.join(filepath, file_name + '.' + file_ext)

            # check if file path exists, otherwise create it, copy file to calibre path and delete temp file
            if not os.path.exists(filepath):
                try:
                    os.makedirs(filepath)
                except OSError:
                    flash(_(u"Failed to create path %(path)s (Permission denied).", path=filepath), category="error")
                    return redirect(url_for('show_book', book_id=book.id))
            try:
                requested_file.save(saved_filename)
            except OSError:
                flash(_(u"Failed to store file %(file)s.", file=saved_filename), category="error")
                return redirect(url_for('show_book', book_id=book.id))

            file_size = os.path.getsize(saved_filename)
            is_format = db.session.query(db.Data).filter(db.Data.book == book_id).\
                filter(db.Data.format == file_ext.upper()).first()

            # Format entry already exists, no need to update the database
            if is_format:
                app.logger.info('Book format already existing')
            else:
                db_format = db.Data(book_id, file_ext.upper(), file_size, file_name)
                db.session.add(db_format)
                db.session.commit()
                db.session.connection().connection.connection.create_function("title_sort", 1, db.title_sort)

            # Queue uploader info
            uploadText=_(u"File format %(ext)s added to %(book)s", ext=file_ext.upper(), book=book.title)
            helper.global_WorkerThread.add_upload(current_user.nickname,
                "<a href=\"" + url_for('show_book', book_id=book.id) + "\">" + uploadText + "</a>")