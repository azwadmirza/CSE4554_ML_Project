    def on_received_payments(self, payments):
        if not payments:
            return
        for payment in payments["payments"]:
            self.add_payment_to_list(payment)