def send_notif_to_attendees(order, purchaser_id):
    for holder in order.ticket_holders:
        if holder.user:
            # send notification if the ticket holder is a registered user.
            if holder.user.id != purchaser_id:
                # The ticket holder is not the purchaser
                send_notification(
                    user=holder.user,
                    action=TICKET_PURCHASED_ATTENDEE,
                    title=NOTIFS[TICKET_PURCHASED_ATTENDEE]['title'].format(
                        event_name=order.event.name
                    ),
                    message=NOTIFS[TICKET_PURCHASED_ATTENDEE]['message'].format(
                        pdf_url=holder.pdf_url
                    )
                )
            else:
                # The Ticket purchaser
                send_notification(
                    user=holder.user,
                    action=TICKET_PURCHASED,
                    title=NOTIFS[TICKET_PURCHASED]['title'].format(
                        invoice_id=order.invoice_number
                    ),
                    message=NOTIFS[TICKET_PURCHASED]['message'].format(
                        order_url=order.tickets_pdf_url
                    )
                )