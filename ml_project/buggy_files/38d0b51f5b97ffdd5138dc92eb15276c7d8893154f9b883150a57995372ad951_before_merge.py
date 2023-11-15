def patch(name,
          source=None,
          hash=None,
          options='',
          dry_run_first=True,
          env=None,
          **kwargs):
    '''
    Apply a patch to a file. Note: a suitable ``patch`` executable must be
    available on the minion when using this state function.

    name
        The file to with the patch will be applied.

    source
        The source patch to download to the minion, this source file must be
        hosted on the salt master server. If the file is located in the
        directory named spam, and is called eggs, the source string is
        salt://spam/eggs. A source is required.

    hash
        Hash of the patched file. If the hash of the target file matches this
        value then the patch is assumed to have been applied. The hash string
        is the hash algorithm followed by the hash of the file:
        md5=e138491e9d5b97023cea823fe17bac22

    options
        Extra options to pass to patch.

    dry_run_first : ``True``
        Run patch with ``--dry-run`` first to check if it will apply cleanly.

    env
        Specify the environment from which to retrieve the patch file indicated
        by the ``source`` parameter. If not provided, this defaults to the
        environment from which the state is being executed.

    Usage:

    .. code-block:: yaml

        # Equivalent to ``patch --forward /opt/file.txt file.patch``
        /opt/file.txt:
          file.patch:
            - source: salt://file.patch
            - hash: md5=e138491e9d5b97023cea823fe17bac22
    '''
    ret = {'name': name, 'changes': {}, 'result': False, 'comment': ''}
    check_res, check_msg = _check_file(name)
    if not check_res:
        return _error(ret, check_msg)
    if not source:
        return _error(ret, 'Source is required')
    if hash is None:
        return _error(ret, 'Hash is required')

    if __salt__['file.check_hash'](name, hash):
        ret.update(result=True, comment='Patch is already applied')
        return ret

    if isinstance(env, salt._compat.string_types):
        msg = (
            'Passing a salt environment should be done using \'saltenv\' not '
            '\'env\'. This warning will go away in Salt Boron and this '
            'will be the default and expected behavior. Please update your '
            'state files.'
        )
        salt.utils.warn_until('Boron', msg)
        ret.setdefault('warnings', []).append(msg)
        # No need to set __env__ = env since that's done in the state machinery

    # get cached file or copy it to cache
    cached_source_path = __salt__['cp.cache_file'](source, __env__)
    if not cached_source_path:
        ret['comment'] = ('Unable to cache {0} from saltenv {1!r}'
                          .format(source, __env__))
        return ret

    log.debug(
        'State patch.applied cached source {0} -> {1}'.format(
            source, cached_source_path
        )
    )

    if dry_run_first or __opts__['test']:
        ret['changes'] = __salt__['file.patch'](
            name, cached_source_path, options=options, dry_run=True
        )
        if __opts__['test']:
            ret['comment'] = 'File {0} will be patched'.format(name)
            ret['result'] = None
            return ret
        if ret['changes']['retcode']:
            return ret

    ret['changes'] = __salt__['file.patch'](
        name, cached_source_path, options=options
    )
    ret['result'] = not ret['changes']['retcode']
    if ret['result'] and not __salt__['file.check_hash'](name, hash):
        ret.update(
            result=False,
            comment='File {0} hash mismatch after patch was applied'.format(
                name
            )
        )
    return ret