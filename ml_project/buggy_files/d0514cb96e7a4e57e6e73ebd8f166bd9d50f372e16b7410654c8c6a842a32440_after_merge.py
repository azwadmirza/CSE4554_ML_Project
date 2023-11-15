def osm_bldg_download(polygon=None, north=None, south=None, east=None, west=None,
                      timeout=180, memory=None, max_query_area_size=50*1000*50*1000):
    """
    Download OpenStreetMap building footprint data.

    Parameters
    ----------
    polygon : shapely Polygon or MultiPolygon
        geographic shape to fetch the building footprints within
    north : float
        northern latitude of bounding box
    south : float
        southern latitude of bounding box
    east : float
        eastern longitude of bounding box
    west : float
        western longitude of bounding box
    timeout : int
        the timeout interval for requests and to pass to API
    memory : int
        server memory allocation size for the query, in bytes. If none, server
        will use its default allocation size
    max_query_area_size : float
        max area for any part of the geometry, in the units the geometry is in:
        any polygon bigger will get divided up for multiple queries to API
        (default is 50,000 * 50,000 units (ie, 50km x 50km in area, if units are
        meters))

    Returns
    -------
    list
        list of response_json dicts
    """

    # check if we're querying by polygon or by bounding box based on which
    # argument(s) where passed into this function
    by_poly = polygon is not None
    by_bbox = not (north is None or south is None or east is None or west is None)
    if not (by_poly or by_bbox):
        raise ValueError('You must pass a polygon or north, south, east, and west')

    response_jsons = []

    # pass server memory allocation in bytes for the query to the API
    # if None, pass nothing so the server will use its default allocation size
    # otherwise, define the query's maxsize parameter value as whatever the
    # caller passed in
    if memory is None:
        maxsize = ''
    else:
        maxsize = '[maxsize:{}]'.format(memory)

    # define the query to send the API
    if by_bbox:
        # turn bbox into a polygon and project to local UTM
        polygon = Polygon([(west, south), (east, south), (east, north), (west, north)])
        geometry_proj, crs_proj = project_geometry(polygon)

        # subdivide it if it exceeds the max area size (in meters), then project
        # back to lat-long
        geometry_proj_consolidated_subdivided = consolidate_subdivide_geometry(geometry_proj, max_query_area_size=max_query_area_size)
        geometry, _ = project_geometry(geometry_proj_consolidated_subdivided, crs=crs_proj, to_latlong=True)
        log('Requesting building footprints data within bounding box from API in {:,} request(s)'.format(len(geometry)))
        start_time = time.time()

        # loop through each polygon rectangle in the geometry (there will only
        # be one if original bbox didn't exceed max area size)
        for poly in geometry:
            # represent bbox as south,west,north,east and round lat-longs to 8
            # decimal places (ie, within 1 mm) so URL strings aren't different
            # due to float rounding issues (for consistent caching)
            west, south, east, north = poly.bounds
            query_template = ('[out:json][timeout:{timeout}]{maxsize};((way["building"]({south:.8f},'
                              '{west:.8f},{north:.8f},{east:.8f});(._;>;););(relation["building"]'
                              '({south:.8f},{west:.8f},{north:.8f},{east:.8f});(._;>;);););out;')
            query_str = query_template.format(north=north, south=south, east=east, west=west, timeout=timeout, maxsize=maxsize)
            response_json = overpass_request(data={'data':query_str}, timeout=timeout)
            response_jsons.append(response_json)
        msg = ('Got all building footprints data within bounding box from '
               'API in {:,} request(s) and {:,.2f} seconds')
        log(msg.format(len(geometry), time.time()-start_time))

    elif by_poly:
        # project to utm, divide polygon up into sub-polygons if area exceeds a
        # max size (in meters), project back to lat-long, then get a list of polygon(s) exterior coordinates
        geometry_proj, crs_proj = project_geometry(polygon)
        geometry_proj_consolidated_subdivided = consolidate_subdivide_geometry(geometry_proj, max_query_area_size=max_query_area_size)
        geometry, _ = project_geometry(geometry_proj_consolidated_subdivided, crs=crs_proj, to_latlong=True)
        polygon_coord_strs = get_polygons_coordinates(geometry)
        log('Requesting building footprints data within polygon from API in {:,} request(s)'.format(len(polygon_coord_strs)))
        start_time = time.time()

        # pass each polygon exterior coordinates in the list to the API, one at
        # a time
        for polygon_coord_str in polygon_coord_strs:
            query_template = ('[out:json][timeout:{timeout}]{maxsize};(way'
                              '(poly:"{polygon}")["building"];(._;>;);relation'
                              '(poly:"{polygon}")["building"];(._;>;););out;')
            query_str = query_template.format(polygon=polygon_coord_str, timeout=timeout, maxsize=maxsize)
            response_json = overpass_request(data={'data':query_str}, timeout=timeout)
            response_jsons.append(response_json)
        msg = ('Got all building footprints data within polygon from API in '
               '{:,} request(s) and {:,.2f} seconds')
        log(msg.format(len(polygon_coord_strs), time.time()-start_time))

    return response_jsons