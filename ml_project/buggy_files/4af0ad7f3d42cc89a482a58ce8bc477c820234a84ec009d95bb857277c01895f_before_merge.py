def run():
    app.run(
        debug=settings['general']['debug'],
        use_debugger=settings['general']['debug'],
        port=settings['server']['port'],
        host=settings['server']['bind_address']
    )