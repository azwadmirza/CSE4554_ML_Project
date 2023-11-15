        def thd():
            url = self.tokenUri
            data = {'redirect_uri': self.loginUri, 'code': code,
                    'grant_type': self.grantType}
            auth = None
            if self.getTokenUseAuthHeaders:
                auth = (self.clientId, self.clientSecret)
            else:
                data.update(
                    {'client_id': self.clientId, 'client_secret': self.clientSecret})
            data.update(self.tokenUriAdditionalParams)
            response = requests.post(
                url, data=data, auth=auth, verify=self.sslVerify)
            response.raise_for_status()
            responseContent = bytes2unicode(response.content)
            try:
                content = json.loads(responseContent)
            except ValueError:
                content = parse_qs(responseContent)
                for k, v in iteritems(content):
                    content[k] = v[0]
            except TypeError:
                content = responseContent

            session = self.createSessionFromToken(content)
            return self.getUserInfoFromOAuthClient(session)