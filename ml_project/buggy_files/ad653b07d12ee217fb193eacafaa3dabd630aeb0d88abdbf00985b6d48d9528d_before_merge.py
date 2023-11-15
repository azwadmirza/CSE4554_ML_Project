def load_pickle(filename):
    """Load a pickle file as a dictionary"""
    try:
        if pd:
            return pd.read_pickle(data), None
        else:
            with open(filename, 'rb') as fid:
                data = pickle.load(fid)
            return data, None
    except Exception as err:
        return None, str(err)