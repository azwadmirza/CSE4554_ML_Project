    def get_checkout_url(order, currency=None, credentials=None):
        if not credentials:
            credentials = PayPalPaymentsManager.get_credentials(order.event)

        if not credentials:
            raise Exception('PayPal credentials have not be set correctly')

        if current_app.config['TESTING']:
            return credentials['CHECKOUT_URL']

        currency = order.event.payment_currency if not currency and order.event.payment_currency != "" else "USD"
        data = {
            'USER': credentials['USER'],
            'PWD': credentials['PWD'],
            'SIGNATURE': credentials['SIGNATURE'],
            'SUBJECT': credentials['EMAIL'],

            'METHOD': 'SetExpressCheckout',
            'VERSION': PayPalPaymentsManager.api_version,
            'PAYMENTREQUEST_0_PAYMENTACTION': 'SALE',
            'PAYMENTREQUEST_0_AMT': order.amount,
            'PAYMENTREQUEST_0_CURRENCYCODE': currency,
            'RETURNURL': make_frontend_url(path='/orders/{identifier}/payment/success'.
                                           format(identifier=order.identifier)),
            'CANCELURL': make_frontend_url(path='/orders/{identifier}/payment/cancelled'.
                                           format(identifier=order.identifier))
        }

        count = 1

        if type(order) is Order:
            for ticket_order in order.order_tickets:
                data['L_PAYMENTREQUEST_' + str(count) + '_NAMEm'] = ticket_order.ticket.name
                data['L_PAYMENTREQUEST_' + str(count) + '_QTYm'] = ticket_order.quantity
                data['L_PAYMENTREQUEST_' + str(count) + '_AMTm'] = ticket_order.ticket.price
                count += 1

        response = requests.post(credentials['SERVER'], data=data)
        if 'TOKEN' not in dict(urlparse.parse_qsl(response.text)):
            raise Exception('PayPal Token could not be retrieved')
        token = dict(urlparse.parse_qsl(response.text))['TOKEN']
        order.paypal_token = token
        save_to_db(order)
        return credentials['CHECKOUT_URL'] + "?" + urlencode({
            'cmd': '_express-checkout',
            'token': token
        })