def query(coord=None, ra=None, dec=None, size=None, naifid=None, pid=None,
          reqkey=None, dataset=2, verbosity=3, return_response=False,
          return_payload=False):
    """
    Query the Spitzer Heritage Archive (SHA).

    Four query types are valid to search by position, NAIFID, PID, and ReqKey::

        position -> search a region
        naifid   -> NAIF ID, which is a unique number allocated to solar
                    system objects (e.g. planets, asteroids, comets,
                    spacecraft) by the NAIF at JPL.
        pid      -> program ID
        reqkey   -> AOR ID: Astronomical Observation Request ID


    For a valid query, enter only parameters related to a single query type::

        position -> ra, dec, size
        naifid   -> naifid
        pid      -> pid
        reqkey   -> reqkey

    Parameters
    ----------
    coord : astropy.coordinates.builtin_systems
        Astropy coordinate object. (query_type = 'position')
    ra : number
        Right ascension in degrees, alternative to using ``coord``.
        (query_type = 'position')
    dec : number
        Declination in degrees, alternative to using ``coord``.
        (query_type = 'position')
    size : number
        Region size in degrees. (query_type = 'position')
    naifid : number
        NAIF ID. (query_type = 'naifid')
    pid : number
        Program ID. (query_type = 'pid')
    reqkey : number
        Astronomical Observation Request ID. (query_type = 'reqkey')
    dataset : number, default 2
        Data set. Valid options::

            1 -> BCD data
            2 -> PBCD data

    verbosity : number, default 3
        Verbosity level, controls the number of columns to output.

    Returns
    -------
    table : `~astropy.table.Table`

    Examples
    --------
    Position query using an astropy coordinate object

    >>> import astropy.coordinates as coord
    >>> import astropy.units as u
    >>> from astroquery import sha
    >>> pos_t = sha.query(coord=coord.FK5(ra=163.6136, dec=-11.784,
    ... unit=(u.degree, u.degree)), size=0.5)

    Position query with optional ``ra`` and ``dec`` parameters

    >>> pos_t = sha.query(ra=163.6136, dec=-11.784, size=0.5)

    NAIFID query

    >>> nid_t = sha.query(naifid=2003226)

    PID query

    >>> pid_t = sha.query(pid=30080)

    ReqKey query

    >>> rqk_t = sha.query(reqkey=21641216)

    Notes
    -----
    For column descriptions, metadata, and other information visit the SHA
    query API_ help page

    .. _API: http://sha.ipac.caltech.edu/applications/Spitzer/SHA/help/doc/api.html
    """
    # Use Coordinate instance if supplied
    if coord is not None:
        try:
            ra = coord.transform_to('fk5').ra.degree
            dec = coord.transform_to('fk5').dec.degree
        except ValueError:
            raise ValueError('Cannot parse `coord` variable.')
    # Query parameters
    payload = {'RA': ra,
               'DEC': dec,
               'SIZE': size,
               'NAIFID': naifid,
               'PID': pid,
               'REQKEY': reqkey,
               'VERB': verbosity,
               'DATASET': 'ivo://irsa.ipac.spitzer.level{0}'.format(dataset)}
    if return_payload:
        return payload
    # Make request
    response = requests.get(uri, params=payload)
    if return_response:
        return response
    response.raise_for_status()
    # Parse output
    # requests returns unicode strings, encode back to ascii
    # because of '|foo|bar|' delimiters, remove first and last empty columns
    raw_data = [line for line in response.text.split('\n')]
    field_widths = [len(s) + 1 for s in raw_data[0].split('|')][1:-1]
    col_names = [s.strip() for s in raw_data[0].split('|')][1:-1]
    type_names = [s.strip() for s in raw_data[1].split('|')][1:-1]
    cs = [0] + np.cumsum(field_widths).tolist()

    def parse_line(line, cs=cs):
        return [line[a:b] for a, b in zip(cs[:-1], cs[1:])]

    data = [parse_line(row) for row in raw_data[4:-1]]
    # Parse type names
    dtypes = _map_dtypes(type_names, field_widths)
    # To table
    # transpose data for appropriate table instance handling
    t = Table(list(zip(*data)), names=col_names, dtype=dtypes)
    return t