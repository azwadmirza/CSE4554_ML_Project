def find_wikidata_id(name, limit=1, session=None):
    """Find the entity ID in wikidata from a title string.

    Args:
        name (str): A string with search terms (eg. "Batman (1989) film")
        limit (int): Number of results to return
        session (requests.Session): requests session to reuse connections

    Returns:
        (str): wikidata entityID corresponding to the title string. 
                  'entityNotFound' will be returned if no page is found
    """

    session = get_session(session=session)

    params = dict(
        action="query",
        list="search",
        srsearch=bytes(name, encoding="utf8"),
        srlimit=limit,
        srprop="",
        format="json",
    )

    try:
        response = session.get(API_URL_WIKIPEDIA, params=params)
        page_id = response.json()["query"]["search"][0]["pageid"]
    except Exception as e:
        # TODO: distinguish between connection error and entity not found
        logger.error("ENTITY NOT FOUND")
        return "entityNotFound"

    params = dict(
        action="query",
        prop="pageprops",
        ppprop="wikibase_item",
        pageids=[page_id],
        format="json",
    )

    try:
        response = session.get(API_URL_WIKIPEDIA, params=params)
        entity_id = response.json()["query"]["pages"][str(page_id)]["pageprops"][
            "wikibase_item"
        ]
    except Exception as e:
        # TODO: distinguish between connection error and entity not found
        logger.error("ENTITY NOT FOUND")
        return "entityNotFound"

    return entity_id