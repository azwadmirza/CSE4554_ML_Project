    def process_tags(db):
        client = local_session(session_factory).client('rds')
        arn = "arn:aws:rds:%s:%s:db:%s" % (region, account_id, db[model.id])
        tag_list = client.list_tags_for_resource(ResourceName=arn)['TagList']
        db['Tags'] = tag_list or []
        return db