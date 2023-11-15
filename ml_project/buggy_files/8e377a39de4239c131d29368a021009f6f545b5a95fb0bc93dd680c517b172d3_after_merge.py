def migrate_Database():
    if not engine.dialect.has_table(engine.connect(), "book_read_link"):
        ReadBook.__table__.create(bind=engine)
    if not engine.dialect.has_table(engine.connect(), "bookmark"):
        Bookmark.__table__.create(bind=engine)
    if not engine.dialect.has_table(engine.connect(), "registration"):
        ReadBook.__table__.create(bind=engine)
        conn = engine.connect()
        conn.execute("insert into registration (domain) values('%.%')")
        session.commit()
    # Handle table exists, but no content
    cnt = session.query(Registration).count()
    if not cnt:
        conn = engine.connect()
        conn.execute("insert into registration (domain) values('%.%')")
        session.commit()
    try:
        session.query(exists().where(Settings.config_use_google_drive)).scalar()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_use_google_drive` INTEGER DEFAULT 0")
        conn.execute("ALTER TABLE Settings ADD column `config_google_drive_folder` String DEFAULT ''")
        conn.execute("ALTER TABLE Settings ADD column `config_google_drive_watch_changes_response` String DEFAULT ''")
        session.commit()
    try:
        session.query(exists().where(Settings.config_columns_to_ignore)).scalar()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_columns_to_ignore` String DEFAULT ''")
        session.commit()
    try:
        session.query(exists().where(Settings.config_default_role)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_default_role` SmallInteger DEFAULT 0")
        session.commit()
    try:
        session.query(exists().where(Settings.config_authors_max)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_authors_max` INTEGER DEFAULT 0")
        session.commit()
    try:
        session.query(exists().where(BookShelf.order)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE book_shelf_link ADD column 'order' INTEGER DEFAULT 1")
        session.commit()
    try:
        session.query(exists().where(Settings.config_rarfile_location)).scalar()
        session.commit()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_rarfile_location` String DEFAULT ''")
        session.commit()
    try:
        create = False
        session.query(exists().where(User.sidebar_view)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE user ADD column `sidebar_view` Integer DEFAULT 1")
        session.commit()
        create = True
    try:
        if create:
            conn = engine.connect()
            conn.execute("SELECT language_books FROM user")
            session.commit()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("UPDATE user SET 'sidebar_view' = (random_books* :side_random + language_books * :side_lang "
            "+ series_books * :side_series + category_books * :side_category + hot_books * "
            ":side_hot + :side_autor + :detail_random)"
            ,{'side_random': SIDEBAR_RANDOM, 'side_lang': SIDEBAR_LANGUAGE, 'side_series': SIDEBAR_SERIES,
            'side_category': SIDEBAR_CATEGORY, 'side_hot': SIDEBAR_HOT, 'side_autor': SIDEBAR_AUTHOR,
            'detail_random': DETAIL_RANDOM})
        session.commit()
    try:
        session.query(exists().where(User.mature_content)).scalar()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("ALTER TABLE user ADD column `mature_content` INTEGER DEFAULT 1")

    if session.query(User).filter(User.role.op('&')(ROLE_ANONYMOUS) == ROLE_ANONYMOUS).first() is None:
        create_anonymous_user()
    try:
        session.query(exists().where(Settings.config_remote_login)).scalar()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_remote_login` INTEGER DEFAULT 0")
    try:
        session.query(exists().where(Settings.config_use_goodreads)).scalar()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_use_goodreads` INTEGER DEFAULT 0")
        conn.execute("ALTER TABLE Settings ADD column `config_goodreads_api_key` String DEFAULT ''")
        conn.execute("ALTER TABLE Settings ADD column `config_goodreads_api_secret` String DEFAULT ''")
    try:
        session.query(exists().where(Settings.config_mature_content_tags)).scalar()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_mature_content_tags` String DEFAULT ''")
    try:
        session.query(exists().where(Settings.config_default_show)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_default_show` SmallInteger DEFAULT 2047")
        session.commit()
    try:
        session.query(exists().where(Settings.config_logfile)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_logfile` String DEFAULT ''")
        session.commit()
    try:
        session.query(exists().where(Settings.config_certfile)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_certfile` String DEFAULT ''")
        conn.execute("ALTER TABLE Settings ADD column `config_keyfile` String DEFAULT ''")
        session.commit()
    try:
        session.query(exists().where(Settings.config_read_column)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_read_column` INTEGER DEFAULT 0")
        session.commit()
    try:
        session.query(exists().where(Settings.config_ebookconverter)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_ebookconverter` INTEGER DEFAULT 0")
        conn.execute("ALTER TABLE Settings ADD column `config_converterpath` String DEFAULT ''")
        conn.execute("ALTER TABLE Settings ADD column `config_calibre` String DEFAULT ''")
        session.commit()
    try:
        session.query(exists().where(Settings.config_theme)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_theme` INTEGER DEFAULT 0")
        session.commit()
    try:
        session.query(exists().where(Settings.config_updatechannel)).scalar()
    except exc.OperationalError:  # Database is not compatible, some rows are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE Settings ADD column `config_updatechannel` INTEGER DEFAULT 0")
        session.commit()


    # Remove login capability of user Guest
    conn = engine.connect()
    conn.execute("UPDATE user SET password='' where nickname = 'Guest' and password !=''")
    session.commit()