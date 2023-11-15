    def before_post(self, args, kwargs, data=None):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event', 'ticket_holders'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            data['status'] = 'pending'