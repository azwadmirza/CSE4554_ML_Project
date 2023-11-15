def create_source_and_submissions(num_submissions=2, num_replies=2):
    # Store source in database
    codename = current_app.crypto_util.genrandomid()
    filesystem_id = current_app.crypto_util.hash_codename(codename)
    journalist_designation = current_app.crypto_util.display_id()
    source = Source(filesystem_id, journalist_designation)
    source.pending = False
    db.session.add(source)
    db.session.commit()

    # Generate submissions directory and generate source key
    os.mkdir(current_app.storage.path(source.filesystem_id))
    current_app.crypto_util.genkeypair(source.filesystem_id, codename)

    # Generate some test submissions
    for _ in range(num_submissions):
        source.interaction_count += 1
        fpath = current_app.storage.save_message_submission(
            source.filesystem_id,
            source.interaction_count,
            source.journalist_filename,
            next(submissions)
        )
        source.last_updated = datetime.datetime.utcnow()
        submission = Submission(source, fpath)
        db.session.add(submission)

    # Generate some test replies
    for _ in range(num_replies):
        source.interaction_count += 1
        fname = "{}-{}-reply.gpg".format(source.interaction_count,
                                         source.journalist_filename)
        current_app.crypto_util.encrypt(
            next(replies),
            [current_app.crypto_util.getkey(source.filesystem_id),
             config.JOURNALIST_KEY],
            current_app.storage.path(source.filesystem_id, fname))

        journalist = Journalist.query.first()
        reply = Reply(journalist, source, fname)
        db.session.add(reply)

    db.session.commit()

    print("Test source (codename: '{}', journalist designation '{}') "
          "added with {} submissions and {} replies".format(
              codename, journalist_designation, num_submissions, num_replies))