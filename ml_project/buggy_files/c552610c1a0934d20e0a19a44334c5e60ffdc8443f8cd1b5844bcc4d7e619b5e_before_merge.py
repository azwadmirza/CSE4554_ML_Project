    def calculate_update_amount(order):
        discount = None
        if order.discount_code_id:
            discount = order.discount
        # Access code part will be done ticket_holders API
        amount = 0
        total_discount = 0
        fees = TicketFees.query.filter_by(currency=order.event.payment_currency).first()

        for order_ticket in order.order_tickets:
            with db.session.no_autoflush:
                if order_ticket.ticket.is_fee_absorbed or not fees:
                    ticket_amount = (order_ticket.ticket.price * order_ticket.quantity)
                    amount += (order_ticket.ticket.price * order_ticket.quantity)
                else:
                    order_fee = fees.service_fee * (order_ticket.ticket.price * order_ticket.quantity) / 100
                    if order_fee > fees.maximum_fee:
                        ticket_amount = (order_ticket.ticket.price * order_ticket.quantity) + fees.maximum_fee
                        amount += (order_ticket.ticket.price * order_ticket.quantity) + fees.maximum_fee
                    else:
                        ticket_amount = (order_ticket.ticket.price * order_ticket.quantity) + order_fee
                        amount += (order_ticket.ticket.price * order_ticket.quantity) + order_fee

                if discount and str(order_ticket.ticket.id) in discount.tickets.split(","):
                    if discount.type == "amount":
                        total_discount += discount.value * order_ticket.quantity
                    else:
                        total_discount += discount.value * ticket_amount / 100

        if discount:
            if discount.type == "amount":
                order.amount = max(amount - total_discount, 0)
            elif discount.type == "percent":
                order.amount = amount - (discount.value * amount / 100.0)
        else:
            order.amount = amount
        save_to_db(order)
        return order