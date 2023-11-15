def get_data(session=None):
    """
    Makes two requests for the current generation total and fuel mix.
    Parses the data into raw form and reads time string associated with it.
    Checks that fuel mix sum is equal to generation total.
    Returns a tuple.
    """

    s = session or requests.Session()
    mixreq = s.get(fuel_mix_url)
    genreq = s.get(current_gen_url)
    mixsoup = BeautifulSoup(mixreq.content, 'html.parser')
    gensoup = BeautifulSoup(genreq.content, 'html.parser')

    try:
        gen_mw = gensoup.find('td', text="MW")
        ts_tag = gen_mw.findNext('td')
        real_ts = ts_tag.text
        gen_total = float(ts_tag.findNext('td').text)

    except AttributeError:
        # No data is available between 12am-1am.
        raise ValueError('No production data is currently available for West Malaysia.')

    mix_header = mixsoup.find('tr', {"class": "gridheader"})
    mix_table = mix_header.find_parent("table")
    rows = mix_table.find_all('tr')
    generation_mix = {}
    for row in rows[1:]:
        cells = row.find_all('td')
        items = [ele.text.strip() for ele in cells]
        generation_mix[items[0]] = float(items[1])

    if sum(generation_mix.values()) == gen_total:
        # Fuel mix matches generation.
        return real_ts, generation_mix
    else:
        raise ValueError('Malaysia generation and fuel mix totals are not equal!')