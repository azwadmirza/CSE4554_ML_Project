    def create_from_data(cls, **kwargs):
        # Convert the datetime for the event's creation
        # appropriately, and include a time zone for it.
        #
        # In the event of any issue, throw it out, and Django will just save
        # the current time.
        try:
            if not isinstance(kwargs['created'], datetime.datetime):
                kwargs['created'] = parse_datetime(kwargs['created'])
            if not kwargs['created'].tzinfo:
                kwargs['created'] = kwargs['created'].replace(tzinfo=utc)
        except (KeyError, ValueError):
            kwargs.pop('created', None)

        sanitize_event_keys(kwargs, cls.VALID_KEYS)
        kwargs.pop('workflow_job_id', None)
        event = cls.objects.create(**kwargs)
        if isinstance(event, AdHocCommandEvent):
            analytics_logger.info(
                'Event data saved.',
                extra=dict(python_objects=dict(job_event=event))
            )
        return event