    def run(self, name, index, username):
        """Create the SearchIndex."""
        es = ElasticsearchDataStore(
            host=current_app.config['ELASTIC_HOST'],
            port=current_app.config['ELASTIC_PORT'])
        user = User.query.filter_by(username=username).first()
        if not user:
            sys.stderr.write('User does not exist\n')
            sys.exit(1)
        if not es.client.indices.exists(index=index):
            sys.stderr.write('Index does not exist in the datastore\n')
            sys.exit(1)
        if SearchIndex.query.filter_by(name=name, index_name=index).first():
            sys.stderr.write(
                'Index with this name already exist in Timesketch\n')
            sys.exit(1)
        searchindex = SearchIndex(
            name=name, description=name, user=user, index_name=index)
        searchindex.grant_permission('read')
        db_session.add(searchindex)
        db_session.commit()
        sys.stdout.write('Search index {0:s} created\n'.format(name))