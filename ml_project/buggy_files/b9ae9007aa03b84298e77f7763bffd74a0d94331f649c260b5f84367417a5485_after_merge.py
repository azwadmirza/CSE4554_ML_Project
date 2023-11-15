def _repo_process_pkg_sls(filename, short_path_name, ret, successful_verbose):
    renderers = salt.loader.render(__opts__, __salt__)

    def _failed_compile(prefix_msg, error_msg):
        log.error('{0} \'{1}\': {2} '.format(prefix_msg, short_path_name, error_msg))
        ret.setdefault('errors', {})[short_path_name] = ['{0}, {1} '.format(prefix_msg, error_msg)]
        return False

    try:
        config = salt.template.compile_template(
            filename,
            renderers,
            __opts__['renderer'],
            __opts__.get('renderer_blacklist', ''),
            __opts__.get('renderer_whitelist', ''))
    except SaltRenderError as exc:
        return _failed_compile('Failed to compile', exc)
    except Exception as exc:
        return _failed_compile('Failed to read', exc)

    if config and isinstance(config, dict):
        revmap = {}
        errors = []
        for pkgname, version_list in six.iteritems(config):
            if pkgname in ret['repo']:
                log.error(
                    'package \'%s\' within \'%s\' already defined, skipping',
                    pkgname, short_path_name
                )
                errors.append('package \'{0}\' already defined'.format(pkgname))
                break
            for version_str, repodata in six.iteritems(version_list):
                # Ensure version is a string/unicode
                if not isinstance(version_str, six.string_types):
                    msg = (
                        'package \'{0}\'{{0}}, version number {1} '
                        'is not a string'.format(pkgname, version_str)
                    )
                    log.error(
                        msg.format(' within \'{0}\''.format(short_path_name))
                    )
                    errors.append(msg.format(''))
                    continue
                # Ensure version contains a dict
                if not isinstance(repodata, dict):
                    msg = (
                        'package \'{0}\'{{0}}, repo data for '
                        'version number {1} is not defined as a dictionary '
                        .format(pkgname, version_str)
                    )
                    log.error(
                        msg.format(' within \'{0}\''.format(short_path_name))
                    )
                    errors.append(msg.format(''))
                    continue
                revmap[repodata['full_name']] = pkgname
        if errors:
            ret.setdefault('errors', {})[short_path_name] = errors
        else:
            ret.setdefault('repo', {}).update(config)
            ret.setdefault('name_map', {}).update(revmap)
            successful_verbose[short_path_name] = config.keys()
    elif config:
        return _failed_compile('Compiled contents', 'not a dictionary/hash')
    else:
        log.debug('No data within \'%s\' after processing', short_path_name)
        # no pkgname found after render
        successful_verbose[short_path_name] = []