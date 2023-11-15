        def generate():
            for event in chain(f(*args, **kwargs), (None,)):
                yield ('data: %s\n\n' % json.dumps(event)).encode()