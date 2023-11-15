    def fromVEvents(cls, events_list, ref=None, **kwargs):
        """
        :type events: list
        """
        assert isinstance(events_list, list)

        vevents = dict()
        if len(events_list) == 1:
            vevents['PROTO'] = events_list[0]  # TODO set mutable = False
        else:
            for event in events_list:
                if 'RECURRENCE-ID' in event:
                    if invalid_timezone(event['RECURRENCE-ID']):
                        default_timezone = kwargs['locale']['default_timezone']
                        recur_id = default_timezone.localize(event['RECURRENCE-ID'].dt)
                        ident = str(to_unix_time(recur_id))
                    else:
                        ident = str(to_unix_time(event['RECURRENCE-ID'].dt))
                    vevents[ident] = event
                else:
                    vevents['PROTO'] = event
        if ref is None:
            ref = 'PROTO'

        try:
            if type(vevents[ref]['DTSTART'].dt) != type(vevents[ref]['DTEND'].dt):  # flake8: noqa
                raise ValueError('DTSTART and DTEND should be of the same type (datetime or date)')
        except KeyError:
            pass

        instcls = cls._get_type_from_vDDD(vevents[ref]['DTSTART'])
        return instcls(vevents, ref=ref, **kwargs)