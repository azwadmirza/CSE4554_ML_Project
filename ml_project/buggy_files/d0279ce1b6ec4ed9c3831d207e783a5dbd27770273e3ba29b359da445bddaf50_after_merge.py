    def update(self):
        self.menu_actions = [('Pay', self.do_pay), ('Details', self.do_view), ('Delete', self.do_delete)]
        invoices_list = self.ids.invoices_container
        invoices_list.clear_widgets()
        _list = self.app.wallet.invoices.sorted_list()
        for pr in _list:
            ci = self.get_card(pr)
            invoices_list.add_widget(ci)