    def run(self, file_path, sketch_id, username, timeline_name):
        """This is the run method."""

        file_path = os.path.realpath(file_path)
        file_path_no_extension, extension = os.path.splitext(file_path)
        extension = extension.lstrip('.')
        filename = os.path.basename(file_path_no_extension)

        supported_extensions = ('plaso', 'csv', 'jsonl')

        if not os.path.isfile(file_path):
            sys.exit('No such file: {0:s}'.format(file_path))

        if extension not in supported_extensions:
            sys.exit(
                'Extension {0:s} is not supported. '
                '(supported extensions are: {1:s})'.format(
                    extension, ', '.join(supported_extensions)))

        user = None
        if not username:
            username = pwd.getpwuid(os.stat(file_path).st_uid).pw_name
        if not username == 'root':
            if not isinstance(username, six.text_type):
                username = codecs.decode(username, 'utf-8')
            user = User.query.filter_by(username=username).first()
        if not user:
            sys.exit('Cannot determine user for file: {0:s}'.format(file_path))

        sketch = None
        # If filename starts with <number> then use that as sketch_id.
        # E.g: 42_file_name.plaso means sketch_id is 42.
        sketch_id_from_filename = filename.split('_')[0]
        if not sketch_id and sketch_id_from_filename.isdigit():
            sketch_id = sketch_id_from_filename

        if sketch_id:
            try:
                sketch = Sketch.query.get_with_acl(sketch_id, user=user)
            except Forbidden:
                pass

        if not timeline_name:
            if not isinstance(timeline_name, six.text_type):
                timeline_name = codecs.decode(timeline_name, 'utf-8')

            timeline_name = timeline_name.replace('_', ' ')
            # Remove sketch ID if present in the filename.
            timeline_parts = timeline_name.split()
            if timeline_parts[0].isdigit():
                timeline_name = ' '.join(timeline_name.split()[1:])

        if not sketch:
            # Create a new sketch.
            sketch_name = 'Sketch for: {0:s}'.format(timeline_name)
            sketch = Sketch(
                name=sketch_name, description=sketch_name, user=user)
            # Need to commit here to be able to set permissions later.
            db_session.add(sketch)
            db_session.commit()
            sketch.grant_permission(permission='read', user=user)
            sketch.grant_permission(permission='write', user=user)
            sketch.grant_permission(permission='delete', user=user)
            sketch.status.append(sketch.Status(user=None, status='new'))
            db_session.add(sketch)
            db_session.commit()

        index_name = uuid.uuid4().hex
        if not isinstance(index_name, six.text_type):
            index_name = codecs.decode(index_name, 'utf-8')

        searchindex = SearchIndex.get_or_create(
            name=timeline_name,
            description=timeline_name,
            user=user,
            index_name=index_name)

        searchindex.grant_permission(permission='read', user=user)
        searchindex.grant_permission(permission='write', user=user)
        searchindex.grant_permission(permission='delete', user=user)

        searchindex.set_status('processing')
        db_session.add(searchindex)
        db_session.commit()

        if sketch and sketch.has_permission(user, 'write'):
            timeline = Timeline(
                name=searchindex.name,
                description=searchindex.description,
                sketch=sketch,
                user=user,
                searchindex=searchindex)
            timeline.set_status('processing')
            sketch.timelines.append(timeline)
            db_session.add(timeline)
            db_session.commit()

        # Start Celery pipeline for indexing and analysis.
        # Import here to avoid circular imports.
        from timesketch.lib import tasks
        pipeline = tasks.build_index_pipeline(
            file_path, timeline_name, index_name, extension, sketch.id)
        pipeline.apply_async(task_id=index_name)

        print('Imported {0:s} to sketch: {1:d} ({2:s})'.format(
            file_path, sketch.id, sketch.name))