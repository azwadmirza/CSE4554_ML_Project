    def lookup():
        replies = []
        source_inbox = Reply.query.filter(Reply.source_id == g.source.id) \
                                  .filter(Reply.deleted_by_source == False).all()  # noqa

        for reply in source_inbox:
            reply_path = current_app.storage.path(
                g.filesystem_id,
                reply.filename,
            )
            try:
                with io.open(reply_path, "rb") as f:
                    contents = f.read()
                reply_obj = current_app.crypto_util.decrypt(g.codename, contents)
                reply.decrypted = reply_obj
            except UnicodeDecodeError:
                current_app.logger.error("Could not decode reply %s" %
                                         reply.filename)
            except FileNotFoundError:
                current_app.logger.error("Reply file missing: %s" %
                                         reply.filename)
            else:
                reply.date = datetime.utcfromtimestamp(
                    os.stat(reply_path).st_mtime)
                replies.append(reply)

        # Sort the replies by date
        replies.sort(key=operator.attrgetter('date'), reverse=True)

        # Generate a keypair to encrypt replies from the journalist
        # Only do this if the journalist has flagged the source as one
        # that they would like to reply to. (Issue #140.)
        if not current_app.crypto_util.get_fingerprint(g.filesystem_id) and \
                g.source.flagged:
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            async_genkey(current_app.crypto_util,
                         db_uri,
                         g.filesystem_id,
                         g.codename)

        return render_template(
            'lookup.html',
            allow_document_uploads=current_app.instance_config.allow_document_uploads,
            codename=g.codename,
            replies=replies,
            flagged=g.source.flagged,
            new_user=session.get('new_user', None),
            haskey=current_app.crypto_util.get_fingerprint(g.filesystem_id),
            form=SubmissionForm(),
        )