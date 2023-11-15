def get_or_create_main_db(caravel):
    db = caravel.db
    config = caravel.app.config
    DB = caravel.models.Database
    logging.info("Creating database reference")
    dbobj = db.session.query(DB).filter_by(database_name='main').first()
    if not dbobj:
        dbobj = DB(database_name="main")
    logging.info(config.get("SQLALCHEMY_DATABASE_URI"))
    dbobj.sqlalchemy_uri = config.get("SQLALCHEMY_DATABASE_URI")
    dbobj.expose_in_sqllab = True
    db.session.add(dbobj)
    db.session.commit()
    return dbobj