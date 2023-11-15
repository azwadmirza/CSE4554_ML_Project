    def run(self, header, body, partial_args, app=None, interval=None,
            countdown=1, max_retries=None, eager=False,
            task_id=None, **options):
        app = app or self._get_app(body)
        group_id = header.options.get('task_id') or uuid()
        root_id = body.options.get('root_id')
        body.chord_size = self.__length_hint__()
        options = dict(self.options, **options) if options else self.options
        if options:
            options.pop('task_id', None)
            body.options.update(options)

        results = header.freeze(
            group_id=group_id, chord=body, root_id=root_id).results
        bodyres = body.freeze(task_id, root_id=root_id)

        # Chains should not be passed to the header tasks. See #3771
        options.pop('chain', None)
        # Neither should chords, for deeply nested chords to work
        options.pop('chord', None)

        parent = app.backend.apply_chord(
            header, partial_args, group_id, body,
            interval=interval, countdown=countdown,
            options=options, max_retries=max_retries,
            result=results)
        bodyres.parent = parent
        return bodyres