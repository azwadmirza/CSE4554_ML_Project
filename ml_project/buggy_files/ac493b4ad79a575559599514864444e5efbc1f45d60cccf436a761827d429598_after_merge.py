        def decorator(callback):
            RTMClient.on(event=event, callback=callback)
            return callback