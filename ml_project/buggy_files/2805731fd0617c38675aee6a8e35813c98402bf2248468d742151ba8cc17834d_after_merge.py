def __virtual__():
    if "elasticsearch.index_exists" not in __salt__:
        return (
            False,
            "Elasticsearch module not availble.  Check that the elasticsearch library is installed.",
        )
    return __virtualname__