def is_picklable(obj: object) -> bool:
    """Tests if an object can be pickled"""

    try:
        pickle.dumps(obj)
        return True
    except pickle.PicklingError:
        return False