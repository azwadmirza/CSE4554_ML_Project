    def on_received_payments(self, payments):
        for payment in payments["payments"]:
            self.add_payment_to_list(payment)