    def _list_tar(name, cached, decompress_cmd, failhard=False):
        '''
        List the contents of a tar archive.
        '''
        dirs = []
        files = []
        links = []
        try:
            open_kwargs = {'name': cached} \
                if not isinstance(cached, subprocess.Popen) \
                else {'fileobj': cached.stdout, 'mode': 'r|'}
            with contextlib.closing(tarfile.open(**open_kwargs)) as tar_archive:
                for member in tar_archive.getmembers():
                    _member = salt.utils.data.decode(member.name)
                    if member.issym():
                        links.append(_member)
                    elif member.isdir():
                        dirs.append(_member + '/')
                    else:
                        files.append(_member)
            return dirs, files, links

        except tarfile.ReadError:
            if failhard:
                if isinstance(cached, subprocess.Popen):
                    stderr = cached.communicate()[1]
                    if cached.returncode != 0:
                        raise CommandExecutionError(
                            'Failed to decompress {0}'.format(name),
                            info={'error': stderr}
                        )
            else:
                if not salt.utils.path.which('tar'):
                    raise CommandExecutionError('\'tar\' command not available')
                if decompress_cmd is not None:
                    # Guard against shell injection
                    try:
                        decompress_cmd = ' '.join(
                            [_quote(x) for x in shlex.split(decompress_cmd)]
                        )
                    except AttributeError:
                        raise CommandExecutionError('Invalid CLI options')
                else:
                    if salt.utils.path.which('xz') \
                            and __salt__['cmd.retcode'](['xz', '-t', cached],
                                                        python_shell=False,
                                                        ignore_retcode=True) == 0:
                        decompress_cmd = 'xz --decompress --stdout'

                if decompress_cmd:
                    decompressed = subprocess.Popen(
                        '{0} {1}'.format(decompress_cmd, _quote(cached)),
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                    return _list_tar(name, decompressed, None, True)

        raise CommandExecutionError(
            'Unable to list contents of {0}. If this is an XZ-compressed tar '
            'archive, install XZ Utils to enable listing its contents. If it '
            'is compressed using something other than XZ, it may be necessary '
            'to specify CLI options to decompress the archive. See the '
            'documentation for details.'.format(name)
        )