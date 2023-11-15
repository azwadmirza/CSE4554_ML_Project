def query_entity_links(entity_id, session=None):
    """Query all linked pages from a wikidata entityID

    Args:
        entity_id (str): A wikidata entity ID
        session (requests.Session): requests session to reuse connections

    Returns:
        (json): dictionary with linked pages.
    """
    query = (
        """
    PREFIX entity: <http://www.wikidata.org/entity/>
    #partial results

    SELECT ?propUrl ?propLabel ?valUrl ?valLabel
    WHERE
    {
        hint:Query hint:optimizer 'None' .
        {	BIND(entity:"""
        + entity_id
        + """ AS ?valUrl) .
            BIND("N/A" AS ?propUrl ) .
            BIND("identity"@en AS ?propLabel ) .
        }
        UNION
        {	entity:"""
        + entity_id
        + """ ?propUrl ?valUrl .
            ?property ?ref ?propUrl .
            ?property rdf:type wikibase:Property .
            ?property rdfs:label ?propLabel
        }

        ?valUrl rdfs:label ?valLabel
        FILTER (LANG(?valLabel) = 'en') .
        OPTIONAL{ ?valUrl wdt:P18 ?picture .}
        FILTER (lang(?propLabel) = 'en' )
    }
    ORDER BY ?propUrl ?valUrl
    LIMIT 500
    """
    )

    session = get_session(session=session)

    try:
        data = session.get(
            API_URL_WIKIDATA, params=dict(query=query, format="json")
        ).json()
    except Exception as e:
        # TODO log exception
        # print(e)
        # print("Entity ID not Found in Wikidata")
        return {}

    return data