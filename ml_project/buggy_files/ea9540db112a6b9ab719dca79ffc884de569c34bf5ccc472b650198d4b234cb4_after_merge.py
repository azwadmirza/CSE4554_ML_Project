def suds_unwrapper(wrapped_data):
    """
    Removes suds wrapping from returned xml data

    When grabbing data via votable_interceptor.last_payload from the
    suds.client.Client module, it returns the xml data in an un-helpful
    "<s:Envelope>" that needs to be removed. This function politely cleans
    it up.

    Parameters
    ----------
    wrapped_data : `str`
        Contains the wrapped xml results from a WSDL query

    Returns
    -------
    unwrapped : `str`
        The xml results with the wrapper removed

    Examples
    --------
    >>> from sunpy.net.helio import hec  Todo: Fix this example!
    >>> from suds.client import Client
    >>> from sunpy.net.proxyfix import WellBehavedHttpTransport
    >>> votable_interceptor = hec.VotableInterceptor()
    >>> client = Client(hec.parser.wsdl_retriever(), plugins=[self.votable_interceptor], transport=WellBehavedHttpTransport())
    >>> client.service.getTableNames()
    >>> temp = client.last_received().str()
    >>> print(temp)
    <?xml version="1.0" encoding="UTF-8"?>
    <S:Envelope ..... >
       <S:Body>
          <helio:queryResponse ... >
             <VOTABLE xmlns="http://www.ivoa.net/xml/VOTable/v1.1" version="1.1">
                <RESOURCE>
                ...
                </RESOURCE>
             </VOTABLE>
          </helio:queryResponse>
       </S:Body>
    </S:Envelope>
    >>> temp = hec.suds_unwrapper(temp)
    >>> print(temp)
    <?xml version="1.0" encoding="UTF-8"?>
    <VOTABLE xmlns="http://www.ivoa.net/xml/VOTable/v1.1" version="1.1">
        <RESOURCE>
        ...
        </RESOURCE>
     </VOTABLE>
    """
    if six.PY3 and not isinstance(wrapped_data, str):
        wrapped_data = wrapped_data.decode("utf-8")
    HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'
    CATCH_1 = '<VOTABLE'
    CATCH_2 = '</VOTABLE>\n'
    # Now going to find the locations of the CATCHes in the wrapped_data
    pos_1 = wrapped_data.find(CATCH_1)
    pos_2 = wrapped_data.find(CATCH_2)
    unwrapped = HEADER + wrapped_data[pos_1:pos_2] + CATCH_2
    return unwrapped