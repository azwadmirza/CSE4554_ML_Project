    def execute_payment(paypal_payer_id, paypal_payment_id):
        """
        Execute payemnt and charge the user.
        :param paypal_payment_id: payment_id
        :param paypal_payer_id: payer_id
        :return: Result of the transaction.
        """

        payment = paypalrestsdk.Payment.find(paypal_payment_id)

        if payment.execute({"payer_id": paypal_payer_id}):
            return True, 'Successfully Executed'
        else:
            return False, payment.error