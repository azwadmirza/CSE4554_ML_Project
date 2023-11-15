def send_email_to_attendees(order, purchaser_id):
    for holder in order.ticket_holders:
        if holder.id != purchaser_id:
            send_email(
                to=holder.email,
                action=TICKET_PURCHASED_ATTENDEE,
                subject=MAILS[TICKET_PURCHASED_ATTENDEE]['subject'].format(
                    event_name=order.event.name,
                    invoice_id=order.invoice_number
                ),
                html=MAILS[TICKET_PURCHASED_ATTENDEE]['message'].format(
                    pdf_url=holder.pdf_url,
                    event_name=order.event.name
                )
            )
        else:
            send_email(
                to=holder.email,
                action=TICKET_PURCHASED,
                subject=MAILS[TICKET_PURCHASED]['subject'].format(
                    event_name=order.event.name,
                    invoice_id=order.invoice_number
                ),
                html=MAILS[TICKET_PURCHASED]['message'].format(
                    pdf_url=holder.pdf_url,
                    event_name=order.event.name
                )
            )