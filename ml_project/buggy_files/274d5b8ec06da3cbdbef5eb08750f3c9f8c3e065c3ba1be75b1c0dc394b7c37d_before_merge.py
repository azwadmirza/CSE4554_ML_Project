    def before_update_object(self, order, data, view_kwargs):
        """
        before update object method of order details
        1. admin can update all the fields.
        2. event organizer
            a. own orders: he/she can update selected fields.
            b. other's orders: can only update the status that too when the order mode is free. No refund system.
        3. order user can update selected fields of his/her order when the status is pending.
        The selected fields mentioned above can be taken from get_updatable_fields method from order model.
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """
        if (not has_access('is_coorganizer', event_id=order.event_id)) and (not current_user.id == order.user_id):
            raise ForbiddenException({'pointer': ''}, "Access Forbidden")

        if has_access('is_coorganizer_but_not_admin', event_id=order.event_id):
            if current_user.id == order.user_id:
                # Order created from the tickets tab.
                for element in data:
                    if data[element] != getattr(order, element, None) and element not in Order.get_updatable_fields():
                        raise ForbiddenException({'pointer': 'data/{}'.format(element)},
                                                 "You cannot update {} of an order".format(element))

            else:
                # Order created from the public pages.
                for element in data:
                    if data[element] != getattr(order, element, None):
                        if element != 'status':
                            raise ForbiddenException({'pointer': 'data/{}'.format(element)},
                                                     "You cannot update {} of an order".format(element))
                        elif element == 'status' and order.amount and order.status == 'completed':
                            # Since we don't have a refund system.
                            raise ForbiddenException({'pointer': 'data/status'},
                                                     "You cannot update the status of a completed paid order")
                        elif element == 'status' and order.status == 'cancelled':
                            # Since the tickets have been unlocked and we can't revert it.
                            raise ForbiddenException({'pointer': 'data/status'},
                                                     "You cannot update the status of a cancelled order")

        elif current_user.id == order.user_id:
            if order.status != 'pending':
                raise ForbiddenException({'pointer': ''},
                                         "You cannot update a non-pending order")
            else:
                for element in data:
                    if data[element] != getattr(order, element, None) and element not in Order.get_updatable_fields():
                        raise ForbiddenException({'pointer': 'data/{}'.format(element)},
                                                 "You cannot update {} of an order".format(element))

        if 'order_notes' in data:
            if order.order_notes and data['order_notes'] not in order.order_notes.split(","):
                data['order_notes'] = '{},{}'.format(order.order_notes, data['order_notes'])