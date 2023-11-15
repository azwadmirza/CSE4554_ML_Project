def housekeeping():
    expired_threshold = request.args.get('expired', default=current_app.config['DEFAULT_EXPIRED_DELETE_HRS'], type=int)
    info_threshold = request.args.get('info', default=current_app.config['DEFAULT_INFO_DELETE_HRS'], type=int)

    has_expired, has_timedout = Alert.housekeeping(expired_threshold, info_threshold)

    errors = []
    for alert in has_expired:
        try:
            alert, _, text, timeout = process_action(alert, action='expired', text='', timeout=current_app.config['ALERT_TIMEOUT'])
            alert = alert.from_expired(text, timeout)
        except RejectException as e:
            write_audit_trail.send(current_app._get_current_object(), event='alert-expire-rejected', message=alert.text,
                                   user=g.login, customers=g.customers, scopes=g.scopes, resource_id=alert.id, type='alert',
                                   request=request)
            errors.append(str(e))
            continue
        except Exception as e:
            raise ApiError(str(e), 500)

        write_audit_trail.send(current_app._get_current_object(), event='alert-expired', message=text, user=g.login,
                               customers=g.customers, scopes=g.scopes, resource_id=alert.id, type='alert', request=request)

    for alert in has_timedout:
        try:
            alert, _, text, timeout = process_action(alert, action='timeout', text='', timeout=current_app.config['ALERT_TIMEOUT'])
            alert = alert.from_timeout(text, timeout)
        except RejectException as e:
            write_audit_trail.send(current_app._get_current_object(), event='alert-timeout-rejected', message=alert.text,
                                   user=g.login, customers=g.customers, scopes=g.scopes, resource_id=alert.id, type='alert',
                                   request=request)
            errors.append(str(e))
            continue
        except Exception as e:
            raise ApiError(str(e), 500)

        write_audit_trail.send(current_app._get_current_object(), event='alert-timeout', message=text, user=g.login,
                               customers=g.customers, scopes=g.scopes, resource_id=alert.id, type='alert', request=request)

    if errors:
        raise ApiError('housekeeping failed', 500, errors=errors)
    else:
        return jsonify(
            status='ok',
            expired=[a.id for a in has_expired],
            timedout=[a.id for a in has_timedout],
            count=len(has_expired) + len(has_timedout)
        )