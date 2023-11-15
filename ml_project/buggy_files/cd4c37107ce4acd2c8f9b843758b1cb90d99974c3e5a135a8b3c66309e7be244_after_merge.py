def main():
    app.logger.info('Starting alerta version %s ...', __version__)
    app.logger.info('Using MongoDB version %s ...', db.get_version())
    app.run(host='0.0.0.0', port=8080, threaded=True)