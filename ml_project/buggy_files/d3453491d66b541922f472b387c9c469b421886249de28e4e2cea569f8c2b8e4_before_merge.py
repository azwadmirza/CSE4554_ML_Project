def on_cleanup(manager, session):
    # Vacuum can take a long time, and is not needed frequently
    persistence = SimplePersistence('db_vacuum')
    last_vacuum = persistence.get('last_vacuum')
    if not last_vacuum or last_vacuum < datetime.now() - VACUUM_INTERVAL:
        log.info('Running VACUUM on database to improve performance and decrease db size.')
        session.execute('VACUUM')
        persistence['last_vacuum'] = datetime.now()