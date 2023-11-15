def _update_repo(ret, target, user, rev, opts):
    log.debug(
            'target {0} is found, '
            '"hg pull && hg up is probably required"'.format(target)
    )

    current_rev = __salt__['hg.revision'](target, user=user)
    if not current_rev:
        return _fail(
                ret,
                'Seems that {0} is not a valid hg repo'.format(target))

    if __opts__['test']:
        test_result = (
                'Repository {0} update is probably required (current '
                'revision is {1})').format(target, current_rev)
        return _neutral_test(
                ret,
                test_result)

    pull_out = __salt__['hg.pull'](target, user=user, opts=opts)

    if rev:
        __salt__['hg.update'](target, rev, user=user)
    else:
        __salt__['hg.update'](target, 'tip', user=user)

    new_rev = __salt__['hg.revision'](cwd=target, user=user)

    if current_rev != new_rev:
        revision_text = '{0} => {1}'.format(current_rev, new_rev)
        log.info(
                'Repository {0} updated: {1}'.format(
                    target, revision_text)
        )
        ret['comment'] = 'Repository {0} updated.'.format(target)
        ret['changes']['revision'] = revision_text
    elif 'error:' in pull_out:
        return _fail(
            ret,
            'An error was thrown by hg:\n{0}'.format(pull_out)
        )
    return ret