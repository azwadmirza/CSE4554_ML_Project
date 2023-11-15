def download_file(url, filename, session=None, headers=None, **kwargs):  # pylint:disable=too-many-return-statements
    """
    Downloads a file specified

    :param url: Source URL
    :param filename: Target file on filesystem
    :param session: request session to use
    :param headers: override existing headers in request session
    :return: True on success, False on failure
    """

    try:
        hooks, cookies, verify, proxies = request_defaults(kwargs)

        with closing(session.get(url, allow_redirects=True, stream=True,
                                 verify=verify, headers=headers, cookies=cookies,
                                 hooks=hooks, proxies=proxies)) as resp:

            if not resp.ok:
                logger.log(u"Requested download url %s returned status code is %s: %s"
                           % (url, resp.status_code, http_code_description(resp.status_code)), logger.DEBUG)
                return False

            try:
                with io.open(filename, 'wb') as fp:
                    for chunk in resp.iter_content(chunk_size=1024):
                        if chunk:
                            fp.write(chunk)
                            fp.flush()

                chmodAsParent(filename)
            except Exception:
                logger.log(u"Problem setting permissions or writing file to: %s" % filename, logger.WARNING)

    except requests.exceptions.RequestException as e:
        remove_file_failed(filename)
        logger.log(u'Error requesting download url: {0}. Error: {1}'.format(url, ex(e)), logger.WARNING)
        return False
    except EnvironmentError as e:
        remove_file_failed(filename)
        logger.log(u"Unable to save the file: %r " % ex(e), logger.WARNING)
        return False
    except Exception:
        remove_file_failed(filename)
        logger.log(u"Unknown exception while loading download URL %s : %r" % (url, traceback.format_exc()), logger.ERROR)
        logger.log(traceback.format_exc(), logger.DEBUG)
        return False

    return True