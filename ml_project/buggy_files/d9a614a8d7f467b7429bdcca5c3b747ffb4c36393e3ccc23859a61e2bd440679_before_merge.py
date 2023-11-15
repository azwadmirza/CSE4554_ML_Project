    def new_func(*args, **kwargs):
        def generate():
            for event in chain(f(*args, **kwargs), (None,)):
                yield 'data: %s\n\n' % json.dumps(event)
        return Response(generate(), mimetype='text/event-stream',
                        direct_passthrough=True)