def _pickle_serialize(obj):
    try:
        return pickle.dumps(obj, protocol=2)
    # Python>=3.5 raises AttributeError here while
    # Python<=3.4 raises pickle.PicklingError
    except (pickle.PicklingError, AttributeError) as e:
        raise ValueError(str(e))