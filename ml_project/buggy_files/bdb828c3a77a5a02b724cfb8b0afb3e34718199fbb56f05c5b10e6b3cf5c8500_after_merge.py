    def __asn_query_parse(text):
        """
        Example:   "23028 | US | arin    | 2002-01-04 | TEAM-CYMRU - Team Cymru
        Inc.,US"
        Exception: "1930  | EU | ripencc |            | RCCN Rede Ciencia
        Tecnologia e Sociedade (RCTS),PT"
        """

        result = {}

        if not text:
            return result

        items = Cymru.__query_parse(text)

        if items[4]:
            # unicode characters need to be decoded explicitly
            # with the help of https://stackoverflow.com/questions/60890590/
            result['as_name'] = items[4].encode('latin1').decode('utf8')

        return result