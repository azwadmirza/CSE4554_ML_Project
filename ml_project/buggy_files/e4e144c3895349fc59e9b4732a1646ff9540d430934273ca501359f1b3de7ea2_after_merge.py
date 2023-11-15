def hypermedia_handler(*args, **kwargs):
    '''
    Determine the best output format based on the Accept header, execute the
    regular handler, and transform the output to the request content type (even
    if it's an error).

    :param args: Pass args through to the main handler
    :param kwargs: Pass kwargs through to the main handler
    '''
    # Execute the real handler. Handle or pass-through any errors we know how
    # to handle (auth & HTTP errors). Reformat any errors we don't know how to
    # handle as a data structure.
    try:
        cherrypy.response.processors = dict(ct_out_map)
        ret = cherrypy.serving.request._hypermedia_inner_handler(*args, **kwargs)
    except (salt.exceptions.EauthAuthenticationError,
            salt.exceptions.TokenAuthenticationError):
        raise cherrypy.HTTPError(401)
    except salt.exceptions.SaltInvocationError:
        raise cherrypy.HTTPError(400)
    except (salt.exceptions.SaltDaemonNotRunning,
            salt.exceptions.SaltReqTimeoutError) as exc:
        raise cherrypy.HTTPError(503, exc.strerror)
    except (cherrypy.TimeoutError if hasattr(cherrypy, 'TimeoutError') else None,
            salt.exceptions.SaltClientTimeout):
        raise cherrypy.HTTPError(504)
    except cherrypy.CherryPyException:
        raise
    except Exception as exc:
        import traceback

        logger.debug("Error while processing request for: %s",
                cherrypy.request.path_info,
                exc_info=True)

        cherrypy.response.status = 500

        ret = {
            'status': cherrypy.response.status,
            'return': '{0}'.format(traceback.format_exc(exc))
                    if cherrypy.config['debug']
                    else "An unexpected error occurred"}

    # Raises 406 if requested content-type is not supported
    best = cherrypy.lib.cptools.accept([i for (i, _) in ct_out_map])

    # Transform the output from the handler into the requested output format
    cherrypy.response.headers['Content-Type'] = best
    out = cherrypy.response.processors[best]
    try:
        response = out(ret)
        if six.PY3:
            response = salt.utils.stringutils.to_bytes(response)
        return response
    except Exception:
        msg = 'Could not serialize the return data from Salt.'
        logger.debug(msg, exc_info=True)
        raise cherrypy.HTTPError(500, msg)