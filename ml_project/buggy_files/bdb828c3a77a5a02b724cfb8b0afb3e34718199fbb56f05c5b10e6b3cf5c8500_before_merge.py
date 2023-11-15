    def __asn_query_parse(text):
        """
        Example:   "23028 | US | arin    | 2002-01-04 | TEAM-CYMRU - Team Cymru
        Inc.,US"
        Exception: "1930  | EU | ripencc |            | RCCN Rede Ciencia
        Tecnologia e Sociedade (RCTS),PT"
        Unicode: "10417 | BR | lacnic | 2000-02-15 | Funda\195\131\194\167\195\131\194\163o de Desenvolvimento da Pesquisa, BR"
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