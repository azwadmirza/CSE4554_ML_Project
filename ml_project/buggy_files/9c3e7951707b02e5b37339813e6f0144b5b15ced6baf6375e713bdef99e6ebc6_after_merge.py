    def wrapped(*args, **kwargs):
        if six.PY2:
            return function(
                *salt.utils.data.decode_list(args),
                **salt.utils.data.decode_dict(kwargs)
            )
        else:
            return function(*args, **kwargs)