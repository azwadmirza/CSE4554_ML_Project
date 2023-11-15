    def requestRaw( self, verb, url, parameters, input ):
        assert verb in [ "HEAD", "GET", "POST", "PATCH", "PUT", "DELETE" ]

        #URLs generated locally will be relative to __base_url
        #URLs returned from the server will start with __base_url
        if url.startswith( self.__base_url ):
            url = url[ len(self.__base_url): ]
        else:
            assert url.startswith( "/" )
        url = self.__prefix + url

        headers = dict()
        if self.__authorizationHeader is not None:
            headers[ "Authorization" ] = self.__authorizationHeader

        if atLeastPython26:
            cnx = self.__connectionClass( host = self.__hostname, port = self.__port, strict = True, timeout = self.__timeout )
        else: #pragma no cover
            cnx = self.__connectionClass( host = self.__hostname, port = self.__port, strict = True ) #pragma no cover
        cnx.request(
            verb,
            self.__completeUrl( url, parameters ),
            json.dumps( input ),
            headers
        )
        response = cnx.getresponse()

        status = response.status
        headers = dict( response.getheaders() )
        output = response.read()

        cnx.close()

        if "x-ratelimit-remaining" in headers and "x-ratelimit-limit" in headers:
            self.rate_limiting = ( int( headers[ "x-ratelimit-remaining" ] ), int( headers[ "x-ratelimit-limit" ] ) )

        # print verb, self.__base_url + url, parameters, input, "==>", status, str( headers ), str( output )
        return status, headers, output