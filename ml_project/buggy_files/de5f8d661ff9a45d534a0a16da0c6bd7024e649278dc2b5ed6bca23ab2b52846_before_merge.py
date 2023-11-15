    def __asn_query(asn):
        query = ASN_QUERY % (asn)
        return list(Cymru.__query(query))[0]  # TODO: we assume there is only one result