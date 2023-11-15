def verify_log(opts):
    '''
    If an insecre logging configuration is found, show a warning
    '''
    level = LOG_LEVELS.get(opts.get('log_level').lower(), logging.NOTSET)

    if level < logging.INFO:
        log.warn('Insecure logging configuration detected! Sensitive data may be logged.')