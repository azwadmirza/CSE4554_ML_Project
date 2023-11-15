def fetch_production(zone_key='CR', session=None,
                     target_datetime=None, logger=logging.getLogger(__name__)):
    # ensure we have an arrow object. if no target_datetime is specified, this defaults to now.
    target_datetime = arrow.get(target_datetime).to(TIMEZONE)

    if target_datetime < arrow.get('2012-07-01'):
        # data availability limit found by manual trial and error
        logger.error('CR API does not provide data before 2012-07-01, '
                     '{} was requested'.format(target_datetime),
                     extra={"key": zone_key})
        return None

    # Do not use existing session as some amount of cache is taking place
    r = requests.session()
    url = 'https://appcenter.grupoice.com/CenceWeb/CencePosdespachoNacional.jsf'
    response = r.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    jsf_view_state = soup.select('#javax.faces.ViewState')[0]['value']

    data = [
        ('formPosdespacho', 'formPosdespacho'),
        ('formPosdespacho:txtFechaInicio_input', target_datetime.format(DATE_FORMAT)),
        ('formPosdespacho:pickFecha', ''),
        ('formPosdespacho:j_idt60_selection', ''),
        ('formPosdespacho:j_idt60_scrollState', '0,1915'),
        ('javax.faces.ViewState', jsf_view_state),
    ]
    response = r.post(url, cookies={}, data=data)

    # tell pandas which table to use by providing CHARACTERISTIC_NAME
    df = pd.read_html(response.text, match=CHARACTERISTIC_NAME, skiprows=1, index_col=0)[0]

    results = df_to_data(zone_key, target_datetime, df, logger)

    return results