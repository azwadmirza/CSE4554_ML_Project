    def _save_auth_data(self, auth_data: dict) -> None:
        self.client.set_header('Authorization', f'Bearer {auth_data["access_token"]}')

        links = auth_data['_links']
        self.query_url = links['ghostflame']['href']
        feed_url_keys = ['events', 'magnitude']
        bills_url_keys = ['bills_summary']
        customer_url_keys = ['customer']

        self.feed_url = self._find_url(feed_url_keys, links)
        self.bills_url = self._find_url(bills_url_keys, links)
        self.customer_url = self._find_url(customer_url_keys, links)