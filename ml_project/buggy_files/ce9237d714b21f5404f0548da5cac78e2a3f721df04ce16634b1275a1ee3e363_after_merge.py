def json_load(datafile: IO) -> Any:
    """
    load data with rapidjson
    Use this to have a consistent experience,
    sete number_mode to "NM_NATIVE" for greatest speed
    """
    return rapidjson.load(datafile, number_mode=rapidjson.NM_NATIVE)