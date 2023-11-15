    def try_payment_action(self, action):
        amount = self.cleaned_data['amount']
        try:
            action(amount.gross)
        except (PaymentError, ValueError) as e:
            self.payment_error(str(e))
            return False
        return True