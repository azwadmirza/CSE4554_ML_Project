    def fake_form(self, bill, project):
        bill.payer_id = self.payer
        bill.amount = self.amount
        bill.what = self.what
        bill.external_link = ""
        bill.date = self.date
        bill.owers = [Person.query.get(ower, project) for ower in self.payed_for]
        bill.original_currency = CurrencyConverter.no_currency
        bill.converted_amount = self.currency_helper.exchange_currency(
            bill.amount, bill.original_currency, project.default_currency
        )

        return bill