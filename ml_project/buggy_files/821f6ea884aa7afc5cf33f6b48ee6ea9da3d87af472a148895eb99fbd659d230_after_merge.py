def send_event_fee_notification():
    from app.instance import current_app as app
    with app.app_context():
        events = Event.query.filter_by(deleted_at=None, state='published').all()
        for event in events:
            latest_invoice = EventInvoice.query.filter_by(
                event_id=event.id).order_by(EventInvoice.created_at.desc()).first()

            if latest_invoice:
                orders = Order.query \
                    .filter_by(event_id=event.id) \
                    .filter_by(status='completed') \
                    .filter(Order.completed_at > latest_invoice.created_at).all()
            else:
                orders = Order.query.filter_by(
                    event_id=event.id).filter_by(status='completed').all()

            fee_total = 0
            for order in orders:
                for ticket in order.tickets:
                    if order.paid_via != 'free' and order.amount > 0 and ticket.price > 0:
                        fee = ticket.price * (get_fee(event.payment_country, order.event.payment_currency) / 100.0)
                        fee_total += fee

            if fee_total > 0:
                owner = get_user_event_roles_by_role_name(event.id, 'owner').first()
                new_invoice = EventInvoice(
                    amount=fee_total, event_id=event.id, user_id=owner.user.id)

                if event.discount_code_id and event.discount_code:
                    r = relativedelta(datetime.datetime.utcnow(), event.created_at)
                    if r <= event.discount_code.valid_till:
                        new_invoice.amount = fee_total - \
                            (fee_total * (event.discount_code.value / 100.0))
                        new_invoice.discount_code_id = event.discount_code_id

                save_to_db(new_invoice)
                prev_month = monthdelta(new_invoice.created_at, 1).strftime(
                    "%b %Y")  # Displayed as Aug 2016
                app_name = get_settings()['app_name']
                frontend_url = get_settings()['frontend_url']
                link = '{}/invoices/{}'.format(frontend_url, new_invoice.identifier)
                send_email_for_monthly_fee_payment(new_invoice.user.email,
                                                   event.name,
                                                   prev_month,
                                                   new_invoice.amount,
                                                   app_name,
                                                   link)
                send_notif_monthly_fee_payment(new_invoice.user,
                                               event.name,
                                               prev_month,
                                               new_invoice.amount,
                                               app_name,
                                               link,
                                               new_invoice.event_id)