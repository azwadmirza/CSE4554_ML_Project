def create_index(sender=None, **kwargs):
    if not os.path.exists(appsettings.WHOOSH_INDEX):
        os.mkdir(appsettings.WHOOSH_INDEX)
        create_source_index()