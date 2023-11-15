def initialize_interfaces(config,app):
    with app.app_context():
        g.default_store = DataStore(config)
        g.mindsdb_native = MindsdbNative(config)