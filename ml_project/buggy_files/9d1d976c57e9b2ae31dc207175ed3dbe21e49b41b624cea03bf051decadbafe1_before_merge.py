    def create_payment(order, return_url, cancel_url):
        """
        Create payment for an order
        :param order: Order to create payment for.
        :param return_url: return url for the payment.
        :param cancel_url: cancel_url for the payment.
        :return: request_id or the error message along with an indicator.
        """
        if (not order.event.paypal_email) or order.event.paypal_email == '':
            raise ConflictException({'pointer': ''}, "Payments through Paypal hasn't been configured for the event")

        PayPalPaymentsManager.configure_paypal()

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url},
            "transactions": [{
                "amount": {
                    "total": int(order.amount*100),
                    "currency": order.event.payment_currency
                },
                "payee": {
                    "email": order.event.paypal_email
                }
            }]
        })

        if payment.create():
            return True, payment.id
        else:
            return False, payment.error