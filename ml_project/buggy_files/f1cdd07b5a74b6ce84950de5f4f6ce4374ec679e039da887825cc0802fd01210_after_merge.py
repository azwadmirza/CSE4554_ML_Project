    def query(self, view_kwargs):
        """
        query method for Attendees List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(TicketHolder)

        if view_kwargs.get('order_identifier'):
            order = safe_query(self, Order, 'identifier', view_kwargs['order_identifier'], 'order_identifier')
            if not has_access('is_registrar', event_id=order.event_id) or not has_access('is_user_itself',
                                                                                         user_id=order.user_id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(Order).filter(Order.id == order.id)

        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            if not has_access('is_registrar', event_id=ticket.event_id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(Ticket).filter(Ticket.id == ticket.id)

        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            if not has_access('is_user_itself', user_id=user.id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(User, User.email == TicketHolder.email).filter(User.id == user.id)

        query_ = event_query(self, query_, view_kwargs, permission='is_registrar')
        return query_