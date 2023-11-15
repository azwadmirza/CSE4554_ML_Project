def migrate_and_get_client_cache(base_folder, out, manager, storage_folder=None):
    # Init paths
    client_cache = ClientCache(base_folder, storage_folder, out)

    # Migration system
    migrator = ClientMigrator(client_cache, Version(CLIENT_VERSION), out, manager)
    migrator.migrate()

    # Init again paths, migration could change config
    client_cache = ClientCache(base_folder, storage_folder, out)
    return client_cache