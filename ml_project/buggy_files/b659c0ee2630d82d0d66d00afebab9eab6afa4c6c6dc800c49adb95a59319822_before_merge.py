    def get_rates(self):
        rates = requests.get(self.api_url).json()["rates"]
        rates[self.default] = 1.0
        return rates