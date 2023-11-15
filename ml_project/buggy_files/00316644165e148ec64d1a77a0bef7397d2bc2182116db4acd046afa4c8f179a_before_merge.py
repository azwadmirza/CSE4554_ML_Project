def should_upgrade(old_database_path, new_database_path, logger=None):
    """
    Decide if we can migrate data from old DB to Pony
    :return: False if something goes wrong, or we don't need/cannot migrate data
    """
    if not os.path.exists(old_database_path):
        # no old DB to upgrade
        return False

    try:
        if not old_db_version_ok(old_database_path):
            return False
    except:
        logger.error("Can't open the old tribler.sdb file")
        return False

    if os.path.exists(new_database_path):
        try:
            cleanup_pony_experimental_db(new_database_path)
            if not new_db_version_ok(new_database_path):
                return False
            if already_upgraded(new_database_path):
                return False
        except:
            logger.error("Error while trying to open Pony DB file ", new_database_path)
            return False

    return True