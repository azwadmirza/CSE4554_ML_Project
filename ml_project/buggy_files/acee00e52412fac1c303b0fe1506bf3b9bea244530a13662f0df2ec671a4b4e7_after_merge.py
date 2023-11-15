def migrate_Database(session):
    engine = session.bind
    if not engine.dialect.has_table(engine.connect(), "book_read_link"):
        ReadBook.__table__.create(bind=engine)
    if not engine.dialect.has_table(engine.connect(), "bookmark"):
        Bookmark.__table__.create(bind=engine)
    if not engine.dialect.has_table(engine.connect(), "kobo_reading_state"):
        KoboReadingState.__table__.create(bind=engine)
    if not engine.dialect.has_table(engine.connect(), "kobo_bookmark"):
        KoboBookmark.__table__.create(bind=engine)
    if not engine.dialect.has_table(engine.connect(), "kobo_statistics"):
        KoboStatistics.__table__.create(bind=engine)
    if not engine.dialect.has_table(engine.connect(), "archived_book"):
        ArchivedBook.__table__.create(bind=engine)
    if not engine.dialect.has_table(engine.connect(), "registration"):
        ReadBook.__table__.create(bind=engine)
        conn = engine.connect()
        conn.execute("insert into registration (domain, allow) values('%.%',1)")
        session.commit()
    try:
        session.query(exists().where(Registration.allow)).scalar()
        session.commit()
    except exc.OperationalError:  # Database is not compatible, some columns are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE registration ADD column 'allow' INTEGER")
        conn.execute("update registration set 'allow' = 1")
        session.commit()
    try:
        session.query(exists().where(RemoteAuthToken.token_type)).scalar()
        session.commit()
    except exc.OperationalError:  # Database is not compatible, some columns are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE remote_auth_token ADD column 'token_type' INTEGER DEFAULT 0")
        conn.execute("update remote_auth_token set 'token_type' = 0")
        session.commit()
    try:
        session.query(exists().where(ReadBook.read_status)).scalar()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("ALTER TABLE book_read_link ADD column 'read_status' INTEGER DEFAULT 0")
        conn.execute("UPDATE book_read_link SET 'read_status' = 1 WHERE is_read")
        conn.execute("ALTER TABLE book_read_link ADD column 'last_modified' DATETIME")
        conn.execute("ALTER TABLE book_read_link ADD column 'last_time_started_reading' DATETIME")
        conn.execute("ALTER TABLE book_read_link ADD column 'times_started_reading' INTEGER DEFAULT 0")
        session.commit()
    test = session.query(ReadBook).filter(ReadBook.last_modified == None).all()
    for book in test:
        book.last_modified = datetime.datetime.utcnow()
    session.commit()
    try:
        session.query(exists().where(Shelf.uuid)).scalar()
    except exc.OperationalError:
        conn = engine.connect()
        conn.execute("ALTER TABLE shelf ADD column 'uuid' STRING")
        conn.execute("ALTER TABLE shelf ADD column 'created' DATETIME")
        conn.execute("ALTER TABLE shelf ADD column 'last_modified' DATETIME")
        conn.execute("ALTER TABLE book_shelf_link ADD column 'date_added' DATETIME")
        for shelf in session.query(Shelf).all():
            shelf.uuid = str(uuid.uuid4())
            shelf.created = datetime.datetime.now()
            shelf.last_modified = datetime.datetime.now()
        for book_shelf in session.query(BookShelf).all():
            book_shelf.date_added = datetime.datetime.now()
        session.commit()
    # Handle table exists, but no content
    cnt = session.query(Registration).count()
    if not cnt:
        conn = engine.connect()
        conn.execute("insert into registration (domain, allow) values('%.%',1)")
        session.commit()
    try:
        session.query(exists().where(BookShelf.order)).scalar()
    except exc.OperationalError:  # Database is not compatible, some columns are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE book_shelf_link ADD column 'order' INTEGER DEFAULT 1")
        session.commit()
    try:
        create = False
        session.query(exists().where(User.sidebar_view)).scalar()
    except exc.OperationalError:  # Database is not compatible, some columns are missing
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
                     ":side_hot + :side_autor + :detail_random)",
                     {'side_random': constants.SIDEBAR_RANDOM, 'side_lang': constants.SIDEBAR_LANGUAGE,
                      'side_series': constants.SIDEBAR_SERIES, 'side_category': constants.SIDEBAR_CATEGORY,
                      'side_hot': constants.SIDEBAR_HOT, 'side_autor': constants.SIDEBAR_AUTHOR,
                      'detail_random': constants.DETAIL_RANDOM})
        session.commit()
    try:
        session.query(exists().where(User.denied_tags)).scalar()
    except exc.OperationalError:  # Database is not compatible, some columns are missing
        conn = engine.connect()
        conn.execute("ALTER TABLE user ADD column `denied_tags` String DEFAULT ''")
        conn.execute("ALTER TABLE user ADD column `allowed_tags` String DEFAULT ''")
        conn.execute("ALTER TABLE user ADD column `denied_column_value` DEFAULT ''")
        conn.execute("ALTER TABLE user ADD column `allowed_column_value` DEFAULT ''")
        session.commit()
    if session.query(User).filter(User.role.op('&')(constants.ROLE_ANONYMOUS) == constants.ROLE_ANONYMOUS).first() \
        is None:
        create_anonymous_user(session)
    try:
        # check if one table with autoincrement is existing (should be user table)
        conn = engine.connect()
        conn.execute("SELECT COUNT(*) FROM sqlite_sequence WHERE name='user'")
    except exc.OperationalError:
        # Create new table user_id and copy contents of table user into it
        conn = engine.connect()
        conn.execute("CREATE TABLE user_id (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                     " nickname VARCHAR(64),"
                     "email VARCHAR(120),"
                     "role SMALLINT,"
                     "password VARCHAR,"
                     "kindle_mail VARCHAR(120),"
                     "locale VARCHAR(2),"
                     "sidebar_view INTEGER,"
                     "default_language VARCHAR(3),"
                     "UNIQUE (nickname),"
                     "UNIQUE (email))")
        conn.execute("INSERT INTO user_id(id, nickname, email, role, password, kindle_mail,locale,"
                     "sidebar_view, default_language) "
                     "SELECT id, nickname, email, role, password, kindle_mail, locale,"
                     "sidebar_view, default_language FROM user")
        # delete old user table and rename new user_id table to user:
        conn.execute("DROP TABLE user")
        conn.execute("ALTER TABLE user_id RENAME TO user")
        session.commit()

    # Remove login capability of user Guest
    conn = engine.connect()
    conn.execute("UPDATE user SET password='' where nickname = 'Guest' and password !=''")
    session.commit()