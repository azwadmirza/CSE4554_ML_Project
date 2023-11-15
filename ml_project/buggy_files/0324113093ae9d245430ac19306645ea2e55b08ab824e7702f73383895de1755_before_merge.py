def _process_requirements(requirements, cmd, cwd, saltenv, user):
    '''
    Process the requirements argument
    '''
    cleanup_requirements = []

    if requirements is not None:
        if isinstance(requirements, string_types):
            requirements = [r.strip() for r in requirements.split(',')]
        elif not isinstance(requirements, list):
            raise TypeError('requirements must be a string or list')

        treq = None

        for requirement in requirements:
            logger.debug('TREQ IS: %s', str(treq))
            if requirement.startswith('salt://'):
                cached_requirements = _get_cached_requirements(
                    requirement, saltenv
                )
                if not cached_requirements:
                    ret = {'result': False,
                           'comment': 'pip requirements file \'{0}\' not found'
                                      .format(requirement)}
                    return None, ret
                requirement = cached_requirements

            if user:
                # Need to make a temporary copy since the user will, most
                # likely, not have the right permissions to read the file

                if not treq:
                    treq = tempfile.mkdtemp()

                __salt__['file.chown'](treq, user, None)

                current_directory = None

                if not current_directory:
                    current_directory = os.path.abspath(os.curdir)

                logger.info('_process_requirements from directory,' +
                            '%s -- requirement: %s', cwd, requirement
                            )

                if cwd is None:
                    r = requirement
                    c = cwd

                    requirement_abspath = os.path.abspath(requirement)
                    cwd = os.path.dirname(requirement_abspath)
                    requirement = os.path.basename(requirement)

                    logger.debug('\n\tcwd: %s -> %s\n\trequirement: %s -> %s\n',
                                 c, cwd, r, requirement
                                 )

                os.chdir(cwd)

                reqs = _resolve_requirements_chain(requirement)

                os.chdir(current_directory)

                logger.info('request files: {0}'.format(str(reqs)))

                for req_file in reqs:

                    req_filename = os.path.basename(req_file)

                    logger.debug('TREQ N CWD: %s -- %s -- for %s', str(treq), str(cwd), str(req_filename))
                    source_path = os.path.join(cwd, req_filename)
                    target_path = os.path.join(treq, req_filename)

                    logger.debug('S: %s', source_path)
                    logger.debug('T: %s', target_path)

                    target_base = os.path.dirname(target_path)

                    if not os.path.exists(target_base):
                        os.makedirs(target_base, mode=0o755)
                        __salt__['file.chown'](target_base, user, None)

                    if not os.path.exists(target_path):
                        logger.debug(
                            'Copying %s to %s', source_path, target_path
                        )
                        __salt__['file.copy'](source_path, target_path)

                    logger.debug(
                        'Changing ownership of requirements file \'{0}\' to '
                        'user \'{1}\''.format(target_path, user)
                    )

                    __salt__['file.chown'](target_path, user, None)

            req_args = os.path.join(treq, requirement) if treq else requirement
            cmd.extend(['--requirement', req_args])

        cleanup_requirements.append(treq)

    logger.debug('CLEANUP_REQUIREMENTS: %s', str(cleanup_requirements))
    return cleanup_requirements, None