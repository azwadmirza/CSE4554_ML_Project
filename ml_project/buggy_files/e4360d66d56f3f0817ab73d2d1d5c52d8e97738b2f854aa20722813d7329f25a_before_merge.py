    def list_users(self):
        result = {}
        # listing all users has always been slower than other operations, why?
        allusers = []
        allusers_details = []
        response = self.get_request(self.root_uri + self.accounts_uri)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        for users in data[u'Members']:
            allusers.append(users[u'@odata.id'])   # allusers[] are URIs

        # for each user, get details
        for uri in allusers:
            response = self.get_request(self.root_uri + uri)
            if response['ret'] is False:
                return response
            data = response['data']

            if not data[u'UserName'] == "":        # only care if name is not empty
                allusers_details.append(dict(
                    Id=data[u'Id'],
                    Name=data[u'Name'],
                    UserName=data[u'UserName'],
                    RoleId=data[u'RoleId']))
        result["entries"] = allusers_details
        return result