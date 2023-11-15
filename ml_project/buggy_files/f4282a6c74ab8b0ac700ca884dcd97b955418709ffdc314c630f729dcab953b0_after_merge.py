    def authenticate_with_qr_code(self, cpf: str, password, uuid: str):
        auth_data = self._password_auth(cpf, password)
        self.headers['Authorization'] = f'Bearer {auth_data["access_token"]}'

        payload = {
            'qr_code_id': uuid,
            'type': 'login-webapp'
        }

        response = requests.post(self.proxy_list_app_url['lift'], json=payload, headers=self.headers)

        auth_data = self._handle_response(response)
        self.headers['Authorization'] = f'Bearer {auth_data["access_token"]}'
        self.feed_url = auth_data['_links']['events']['href']
        self.query_url = auth_data['_links']['ghostflame']['href']
        self.bills_url = auth_data['_links']['bills_summary']['href']