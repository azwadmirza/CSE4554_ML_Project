    def fill(self, bill, project):
        self.payer.data = bill.payer_id
        self.amount.data = bill.amount
        self.what.data = bill.what
        self.external_link.data = bill.external_link
        self.original_currency.data = bill.original_currency
        self.date.data = bill.date
        self.payed_for.data = [int(ower.id) for ower in bill.owers]

        self.original_currency.label = Label("original_currency", _("Currency"))
        self.original_currency.description = _(
            "Project default: %(currency)s",
            currency=render_localized_currency(
                project.default_currency, detailed=False
            ),
        )