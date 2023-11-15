def download_models(content_model_path=DEFAULT_CONTENT_MODEL_PATH,
                    subject_model_path=DEFAULT_SUBJECT_MODEL_PATH,
                    twentysixhundred_model_path=DEFAULT_2600_MODEL_PATH,
                    on_error=None):
    """Download models

    Calls on_error(primary_message, secondary_message) in case of error

    Returns success as boolean value
    """
    from urllib2 import urlopen, URLError, HTTPError
    from httplib import HTTPException
    import socket
    for (url, fn) in ((URL_CLINTON_SUBJECT, subject_model_path),
                      (URL_CLINTON_CONTENT, content_model_path),
                      (URL_2600, twentysixhundred_model_path)):
        if os.path.exists(fn):
            logger.debug('File %s already exists', fn)
            continue
        logger.info('Downloading %s to %s', url, fn)
        try:
            resp = urlopen(url, cafile=CA_BUNDLE)
            with open(fn, 'wb') as f:
                f.write(resp.read())
        except (URLError, HTTPError, HTTPException, socket.error) as exc:
            msg = _('Downloading url failed: %s') % url
            msg2 = '{}: {}'.format(type(exc).__name__, exc)
            logger.exception(msg)
            if on_error:
                on_error(msg, msg2)
            from bleachbit.FileUtilities import delete
            delete(fn, ignore_missing=True)  # delete any partial download
            return False
    return True