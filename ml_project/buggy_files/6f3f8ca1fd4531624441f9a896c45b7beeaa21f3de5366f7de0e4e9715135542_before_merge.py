def grant_exists(grant,
                database,
                user,
                host='localhost',
                grant_option=False,
                escape=True,
                **connection_args):
    '''
    Checks to see if a grant exists in the database

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.grant_exists \
             'SELECT,INSERT,UPDATE,...' 'database.*' 'frank' 'localhost'
    '''
    try:
        target = __grant_generate(
            grant, database, user, host, grant_option, escape
        )
    except Exception:
        log.error('Error during grant generation.')
        return False

    grants = user_grants(user, host, **connection_args)

    if grants is False:
        log.debug('Grant does not exist, or is perhaps not ordered properly?')
        return False

    target_tokens = None
    for grant in grants:
        try:
            if not target_tokens:  # Avoid the overhead of re-calc in loop
                target_tokens = _grant_to_tokens(target)
            grant_tokens = _grant_to_tokens(grant)
            if grant_tokens['user'] == target_tokens['user'] and \
                    grant_tokens['database'] == target_tokens['database'] and \
                    grant_tokens['host'] == target_tokens['host'] and \
                    set(grant_tokens['grant']) == set(target_tokens['grant']):
                return True
            else:
                log.debug('grants mismatch {0!r}<>{1!r}'.format(
                    grant_tokens,
                    target_tokens
                ))

        except Exception as exc:  # Fallback to strict parsing
            log.exception(exc)
            if grants is not False and target in grants:
                log.debug('Grant exists.')
                return True

    log.debug('Grant does not exist, or is perhaps not ordered properly?')
    return False