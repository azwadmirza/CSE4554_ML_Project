def update_pricing(kwargs=None, call=None):
    '''
    Download most recent pricing information from GCE and save locally

    CLI Examples:

    .. code-block:: bash

        salt-cloud -f update_pricing my-gce-config

    .. versionadded:: 2015.8.0
    '''
    url = 'https://cloudpricingcalculator.appspot.com/static/data/pricelist.json'
    price_json = http.query(url, decode=True, decode_type='json')

    outfile = os.path.join(
        __opts__['cachedir'], 'gce-pricing.p'
    )
    with salt.utils.fopen(outfile, 'w') as fho:
        msgpack.dump(price_json['dict'], fho)

    return True