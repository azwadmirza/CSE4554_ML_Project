def send_notif_to_attendees(order, purchaser_id):
    for holder in order.ticket_holders:
        if holder.id != purchaser_id:
            send_notification(
                user=holder,
                action=TICKET_PURCHASED_ATTENDEE,
                title=NOTIFS[TICKET_PURCHASED_ATTENDEE]['title'].format(
                    event_name=order.event.name
                ),
                message=NOTIFS[TICKET_PURCHASED_ATTENDEE]['message'].format(
                    pdf_url=holder.pdf_url
                )
            )
        else:
            send_notification(
                user=holder,
                action=TICKET_PURCHASED,
                title=NOTIFS[TICKET_PURCHASED]['title'].format(
                    invoice_id=order.invoice_number
                ),
                message=NOTIFS[TICKET_PURCHASED]['message'].format(
                    pdf_url=holder.pdf_url
                )
            )