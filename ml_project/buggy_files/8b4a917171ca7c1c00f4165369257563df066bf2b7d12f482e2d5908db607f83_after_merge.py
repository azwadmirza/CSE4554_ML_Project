    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ObjectNotFound({'parameter': 'event_id'},
                                 "Event: {} not found".format(data['event']))

        if get_count(db.session.query(Ticket.id).filter_by(name=data['name'], event_id=int(data['event']),
                                                           deleted_at=None)) > 0:
            raise ConflictException({'pointer': '/data/attributes/name'}, "Ticket already exists")

        if get_count(db.session.query(Event).filter_by(id=int(data['event']), is_ticketing_enabled=False)) > 0:
            raise MethodNotAllowed({'parameter': 'event_id'}, "Ticketing is disabled for this Event")