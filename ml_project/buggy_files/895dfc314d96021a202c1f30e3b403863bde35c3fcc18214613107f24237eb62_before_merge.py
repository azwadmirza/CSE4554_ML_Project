    def setup_logging(app):
        del app.logger.handlers[:]

        # for key in logging.Logger.manager.loggerDict:
        #     print(key)

        loggers = [
            app.logger,
            logging.getLogger('alerta'),  # ??
            # logging.getLogger('flask'),  # ??
            logging.getLogger('flask_compress'),  # ??
            # logging.getLogger('flask_cors'),  # ??
            logging.getLogger('pymongo'),  # ??
            logging.getLogger('raven'),  # ??
            logging.getLogger('requests'),  # ??
            logging.getLogger('sentry'),  # ??
            logging.getLogger('urllib3'),  # ??
            logging.getLogger('werkzeug'),  # ??
        ]

        if app.debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        if app.config['LOG_FILE']:
            from logging.handlers import RotatingFileHandler
            handler = RotatingFileHandler(
                filename=app.config['LOG_FILE'],
                maxBytes=app.config['LOG_MAX_BYTES'],
                backupCount=app.config['LOG_BACKUP_COUNT']
            )
            handler.setLevel(log_level)
            handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        else:
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))

        for logger in loggers:
            logger.addHandler(handler)
            logger.setLevel(log_level)
            logger.propagate = True