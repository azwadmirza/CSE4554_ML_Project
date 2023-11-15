    def before_get(self, args, kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if kwargs.get('order_identifier'):
            order = safe_query(db, Order, 'identifier', kwargs['order_identifier'], 'order_identifier')
            kwargs['id'] = order.id
        elif kwargs.get('id'):
            order = safe_query(db, Order, 'id', kwargs['id'], 'id')

        if not has_access('is_coorganizer', event_id=order.event_id, user_id=order.user_id):
            return ForbiddenException({'source': ''}, 'You can only access your orders or your event\'s orders')