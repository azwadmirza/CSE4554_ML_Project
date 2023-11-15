    def getUserInfo(self, userId):
        """
        This function returns all user info for a given userid/object.
        
        :param userId: The userid of the object
        :type userId: string
        :return: A dictionary with the keys defined in self.userinfo
        :rtype: dict
        """
        ret = {}
        self._bind()
        
        if self.uidtype.lower() == "dn":
            # encode utf8, so that also german ulauts work in the DN
            self.l.search(search_base=to_utf8(userId),
                          search_scope=self.scope,
                          search_filter="(&" + self.searchfilter + ")",
                          attributes=self.userinfo.values())
        else:
            filter = "(&%s(%s=%s))" %\
                (self.searchfilter, self.uidtype, userId)
            self.l.search(search_base=self.basedn,
                              search_scope=self.scope,
                              search_filter=filter,
                              attributes=self.userinfo.values())

        r = self.l.response
        r = self._trim_result(r)
        if len(r) > 1:  # pragma: no cover
            raise Exception("Found more than one object for uid %r" % userId)

        for entry in r:
            attributes = entry.get("attributes")
            ret = self._ldap_attributes_to_user_object(attributes)

        return ret