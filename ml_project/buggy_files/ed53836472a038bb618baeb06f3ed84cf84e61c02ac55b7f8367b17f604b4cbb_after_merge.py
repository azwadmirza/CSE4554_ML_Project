    def handle(self, *args, **options):

        engine = create_engine(get_default_db_string(), convert_unicode=True)

        metadata = MetaData()

        app_config = apps.get_app_config('content')
        # Exclude channelmetadatacache in case we are reflecting an older version of Kolibri
        table_names = [model._meta.db_table for name, model in app_config.models.items() if name != 'channelmetadatacache']
        metadata.reflect(bind=engine, only=table_names)
        Base = automap_base(metadata=metadata)
        # TODO map relationship backreferences using the django names
        Base.prepare()
        session = sessionmaker(bind=engine, autoflush=False)()

        # Load fixture data into the test database with Django
        call_command('loaddata', 'content_import_test.json', interactive=False)

        def get_dict(item):
            value = {key: value for key, value in item.__dict__.items() if key != '_sa_instance_state'}
            return value

        data = {}

        for table_name, record in Base.classes.items():
            data[table_name] = [get_dict(r) for r in session.query(record).all()]

        with open(SCHEMA_PATH_TEMPLATE.format(name=options['version']), 'wb') as f:
            pickle.dump(metadata, f, protocol=2)

        with open(DATA_PATH_TEMPLATE.format(name=options['version']), 'w') as f:
            json.dump(data, f)