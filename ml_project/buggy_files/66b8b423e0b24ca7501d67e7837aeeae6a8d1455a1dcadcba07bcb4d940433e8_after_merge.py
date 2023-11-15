def _rds_tags(
        model, dbs, session_factory, executor_factory, arn_generator):
    """Augment rds instances with their respective tags."""

    def process_tags(db):
        client = local_session(session_factory).client('rds')
        arn = arn_generator.generate(db[model.id])
        tag_list = client.list_tags_for_resource(ResourceName=arn)['TagList']
        db['Tags'] = tag_list or []
        return db

    # Rds maintains a low api call limit, so this can take some time :-(
    with executor_factory(max_workers=1) as w:
        list(w.map(process_tags, dbs))