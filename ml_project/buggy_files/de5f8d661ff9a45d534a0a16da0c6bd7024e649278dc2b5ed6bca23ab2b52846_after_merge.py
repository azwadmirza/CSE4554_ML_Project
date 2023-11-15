    def __asn_query(asn):
        """
        Querys ASN to get CC, registry, AS-name.

        Returns string object of first result in case of success
        or None if there's no result.

        TODO: Handle multiple results
        See https://github.com/certtools/intelmq/issues/543
        """
        query_string = ASN_QUERY % (asn)
        query = list(Cymru.__query(query_string))
        if query:
            return query[0]