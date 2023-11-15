    def create():
        filesystem_id = current_app.crypto_util.hash_codename(
            session['codename'])

        source = Source(filesystem_id, current_app.crypto_util.display_id())
        db.session.add(source)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(
                "Attempt to create a source with duplicate codename: %s" %
                (e,))

            # Issue 2386: don't log in on duplicates
            del session['codename']
            abort(500)
        else:
            os.mkdir(current_app.storage.path(filesystem_id))

        session['logged_in'] = True
        return redirect(url_for('.lookup'))