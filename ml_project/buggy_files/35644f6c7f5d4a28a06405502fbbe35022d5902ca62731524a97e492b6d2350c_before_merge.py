    def request(self, method, url, **kwargs):
        kwargs.setdefault("params", {
            "access_token": self.token,
        })
        r = requests.request(
            method=method,
            url=url,
            **kwargs
        )
        r.raise_for_status()
        json = r.json()
        if check_error(json):
            return json