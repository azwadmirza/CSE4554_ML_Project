    def process_tags(db):
        client = local_session(session_factory).client('rds')
        arn = arn_generator.generate(db[model.id])
        tag_list = client.list_tags_for_resource(ResourceName=arn)['TagList']
        db['Tags'] = tag_list or []
        return db