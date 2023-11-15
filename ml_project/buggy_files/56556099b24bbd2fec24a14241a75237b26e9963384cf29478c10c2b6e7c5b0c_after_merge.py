    def after_create_object(self, order, data, view_kwargs):
        """
        after create object method for OrderListPost Class
        :param order: Object created from mashmallow_jsonapi
        :param data:
        :param view_kwargs:
        :return:
        """
        order_tickets = {}
        for holder in order.ticket_holders:
            if holder.id != current_user.id:
                pdf = create_save_pdf(render_template('pdf/ticket_attendee.html', order=order, holder=holder),
                                      UPLOAD_PATHS['pdf']['ticket_attendee'],
                                      dir_path='/static/uploads/pdf/tickets/')
            else:
                pdf = create_save_pdf(render_template('pdf/ticket_purchaser.html', order=order),
                                      UPLOAD_PATHS['pdf']['ticket_attendee'],
                                      dir_path='/static/uploads/pdf/tickets/')
            holder.pdf_url = pdf
            save_to_db(holder)
            if not order_tickets.get(holder.ticket_id):
                order_tickets[holder.ticket_id] = 1
            else:
                order_tickets[holder.ticket_id] += 1
        for ticket in order_tickets:
            od = OrderTicket(order_id=order.id, ticket_id=ticket, quantity=order_tickets[ticket])
            save_to_db(od)
        order.quantity = order.tickets_count
        order.user = current_user
        save_to_db(order)
        if not has_access('is_coorganizer', event_id=data['event']):
            TicketingManager.calculate_update_amount(order)

        # send e-mail and notifications if the order status is completed
        if order.status == 'completed':
            send_email_to_attendees(order, current_user.id)
            send_notif_to_attendees(order, current_user.id)

            order_url = make_frontend_url(path='/orders/{identifier}'.format(identifier=order.identifier))
            for organizer in order.event.organizers:
                send_notif_ticket_purchase_organizer(organizer, order.invoice_number, order_url, order.event.name)

        data['user_id'] = current_user.id