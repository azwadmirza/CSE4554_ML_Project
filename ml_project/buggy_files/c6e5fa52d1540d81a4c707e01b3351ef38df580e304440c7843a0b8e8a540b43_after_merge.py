def query_entity_description(entity_id, session=None):
    """Query entity wikidata description from entityID

    Args:
        entity_id (str): A wikidata page ID.
        session (requests.Session): requests session to reuse connections

    Returns:
        (str): Wikidata short description of the entityID
               descriptionNotFound' will be returned if no 
               description is found
    """
    query = (
        """
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX schema: <http://schema.org/>

    SELECT ?o
    WHERE 
    {
      wd:"""
        + entity_id
        + """ schema:description ?o.
      FILTER ( lang(?o) = "en" )
    }
    """
    )

    session = get_session(session=session)

    try:
        r = session.get(API_URL_WIKIDATA, params=dict(query=query, format="json"))
        description = r.json()["results"]["bindings"][0]["o"]["value"]
    except Exception as e:
        logger.error("DESCRIPTION NOT FOUND")
        return "descriptionNotFound"

    return description