    def after_create_object(self, order, data, view_kwargs):
        """
        after create object method for OrderListPost Class
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """
        order_tickets = {}
        for holder in order.ticket_holders:
            if holder.id != current_user.id:
                pdf = create_save_pdf(render_template('/pdf/ticket_attendee.html', order=order, holder=holder))
            else:
                pdf = create_save_pdf(render_template('/pdf/ticket_purchaser.html', order=order))
            holder.pdf_url = pdf
            save_to_db(holder)
            if order_tickets.get(holder.ticket_id) is None:
                order_tickets[holder.ticket_id] = 1
            else:
                order_tickets[holder.ticket_id] += 1
        for ticket in order_tickets:
            od = OrderTicket(order_id=order.id, ticket_id=ticket, quantity=order_tickets[ticket])
            save_to_db(od)
        order.quantity = order.get_tickets_count()
        save_to_db(order)
        if not has_access('is_coorganizer', event_id=data['event']):
            TicketingManager.calculate_update_amount(order)
        send_email_to_attendees(order, current_user.id)
        send_notif_to_attendees(order, current_user.id)

        order_url = make_frontend_url(path='/orders/{identifier}'.format(identifier=order.identifier))
        for organizer in order.event.organizers:
            send_notif_ticket_purchase_organizer(organizer, order.invoice_number, order_url, order.event.name)

        data['user_id'] = current_user.id