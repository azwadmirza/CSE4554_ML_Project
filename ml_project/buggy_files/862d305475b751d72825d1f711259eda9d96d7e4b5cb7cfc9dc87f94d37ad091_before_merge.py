def extract_hidden_values(req):
    """
    Gets current aspx page values to enable post requests to be sent.
    Returns a dictionary.
    """

    soup = BeautifulSoup(req.content, 'html.parser')

    # Find and define parameters needed to send a POST request.
    viewstategenerator = soup.find("input", attrs={'id': '__VIEWSTATEGENERATOR'})['value']
    viewstate = soup.find("input", attrs={'id': '__VIEWSTATE'})['value']
    eventvalidation = soup.find("input", attrs={'id': '__EVENTVALIDATION'})['value']
    jschartviewerstate = soup.find("input", attrs={'id': 'MainContent_ctl17_JsChartViewerState'})['value']

    hidden_values = {'viewstategenerator': viewstategenerator,
                     'viewstate': viewstate,
                     'eventvalidation': eventvalidation,
                     'jschartviewerstate': jschartviewerstate}

    return hidden_values