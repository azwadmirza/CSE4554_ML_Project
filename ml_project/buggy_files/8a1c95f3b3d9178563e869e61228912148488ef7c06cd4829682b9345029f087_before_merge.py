def list_(name,
          archive_format=None,
          options=None,
          strip_components=None,
          clean=False,
          verbose=False,
          saltenv='base',
          source_hash=None):
    '''
    .. versionadded:: 2016.11.0
    .. versionchanged:: 2016.11.2
        The rarfile_ Python module is now supported for listing the contents of
        rar archives. This is necessary on minions with older releases of the
        ``rar`` CLI tool, which do not support listing the contents in a
        parsable format.

    .. _rarfile: https://pypi.python.org/pypi/rarfile

    List the files and directories in an tar, zip, or rar archive.

    .. note::
        This function will only provide results for XZ-compressed archives if
        the xz_ CLI command is available, as Python does not at this time
        natively support XZ compression in its tarfile_ module. Keep in mind
        however that most Linux distros ship with xz_ already installed.

        To check if a given minion has xz_, the following Salt command can be
        run:

        .. code-block:: bash

            salt minion_id cmd.which xz

        If ``None`` is returned, then xz_ is not present and must be installed.
        It is widely available and should be packaged as either ``xz`` or
        ``xz-utils``.

    name
        Path/URL of archive

    archive_format
        Specify the format of the archive (``tar``, ``zip``, or ``rar``). If
        this argument is omitted, the archive format will be guessed based on
        the value of the ``name`` parameter.

    options
        **For tar archives only.** This function will, by default, try to use
        the tarfile_ module from the Python standard library to get a list of
        files/directories. If this method fails, then it will fall back to
        using the shell to decompress the archive to stdout and pipe the
        results to ``tar -tf -`` to produce a list of filenames. XZ-compressed
        archives are already supported automatically, but in the event that the
        tar archive uses a different sort of compression not supported natively
        by tarfile_, this option can be used to specify a command that will
        decompress the archive to stdout. For example:

        .. code-block:: bash

            salt minion_id archive.list /path/to/foo.tar.gz options='gzip --decompress --stdout'

        .. note::
            It is not necessary to manually specify options for gzip'ed
            archives, as gzip compression is natively supported by tarfile_.

    strip_components
        This argument specifies a number of top-level directories to strip from
        the results. This is similar to the paths that would be extracted if
        ``--strip-components`` (or ``--strip``) were used when extracting tar
        archives.

        .. versionadded:: 2016.11.2

    clean : False
        Set this value to ``True`` to delete the path referred to by ``name``
        once the contents have been listed. This option should be used with
        care.

        .. note::
            If there is an error listing the archive's contents, the cached
            file will not be removed, to allow for troubleshooting.

    verbose : False
        If ``False``, this function will return a list of files/dirs in the
        archive. If ``True``, it will return a dictionary categorizing the
        paths into separate keys containing the directory names, file names,
        and also directories/files present in the top level of the archive.

        .. versionchanged:: 2016.11.2
            This option now includes symlinks in their own list. Before, they
            were included with files.

    saltenv : base
        Specifies the fileserver environment from which to retrieve
        ``archive``. This is only applicable when ``archive`` is a file from
        the ``salt://`` fileserver.

    source_hash
        If ``name`` is an http(s)/ftp URL and the file exists in the minion's
        file cache, this option can be passed to keep the minion from
        re-downloading the archive if the cached copy matches the specified
        hash.

        .. versionadded:: 2018.3.0

    .. _tarfile: https://docs.python.org/2/library/tarfile.html
    .. _xz: http://tukaani.org/xz/

    CLI Examples:

    .. code-block:: bash

            salt '*' archive.list /path/to/myfile.tar.gz
            salt '*' archive.list /path/to/myfile.tar.gz strip_components=1
            salt '*' archive.list salt://foo.tar.gz
            salt '*' archive.list https://domain.tld/myfile.zip
            salt '*' archive.list https://domain.tld/myfile.zip source_hash=f1d2d2f924e986ac86fdf7b36c94bcdf32beec15
            salt '*' archive.list ftp://10.1.2.3/foo.rar
    '''
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
                    if member.issym():
                        links.append(member.name)
                    elif member.isdir():
                        dirs.append(member.name + '/')
                    else:
                        files.append(member.name)
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

    def _list_zip(name, cached):
        '''
        List the contents of a zip archive.
        Password-protected ZIP archives can still be listed by zipfile, so
        there is no reason to invoke the unzip command.
        '''
        dirs = set()
        files = []
        links = []
        try:
            with contextlib.closing(zipfile.ZipFile(cached)) as zip_archive:
                for member in zip_archive.infolist():
                    path = member.filename
                    if salt.utils.platform.is_windows():
                        if path.endswith('/'):
                            # zipfile.ZipInfo objects on windows use forward
                            # slash at end of the directory name.
                            dirs.add(path)
                        else:
                            files.append(path)
                    else:
                        mode = member.external_attr >> 16
                        if stat.S_ISLNK(mode):
                            links.append(path)
                        elif stat.S_ISDIR(mode):
                            dirs.add(path)
                        else:
                            files.append(path)

                _files = copy.deepcopy(files)
                for path in _files:
                    # ZIP files created on Windows do not add entries
                    # to the archive for directories. So, we'll need to
                    # manually add them.
                    dirname = ''.join(path.rpartition('/')[:2])
                    if dirname:
                        dirs.add(dirname)
                        if dirname in files:
                            files.remove(dirname)
            return list(dirs), files, links
        except zipfile.BadZipfile:
            raise CommandExecutionError('{0} is not a ZIP file'.format(name))

    def _list_rar(name, cached):
        '''
        List the contents of a rar archive.
        '''
        dirs = []
        files = []
        if HAS_RARFILE:
            with rarfile.RarFile(cached) as rf:
                for member in rf.infolist():
                    path = member.filename.replace('\\', '/')
                    if member.isdir():
                        dirs.append(path + '/')
                    else:
                        files.append(path)
        else:
            if not salt.utils.path.which('rar'):
                raise CommandExecutionError(
                    'rar command not available, is it installed?'
                )
            output = __salt__['cmd.run'](
                ['rar', 'lt', name],
                python_shell=False,
                ignore_retcode=False)
            matches = re.findall(r'Name:\s*([^\n]+)\s*Type:\s*([^\n]+)', output)
            for path, type_ in matches:
                if type_ == 'Directory':
                    dirs.append(path + '/')
                else:
                    files.append(path)
            if not dirs and not files:
                raise CommandExecutionError(
                    'Failed to list {0}, is it a rar file? If so, the '
                    'installed version of rar may be too old to list data in '
                    'a parsable format. Installing the rarfile Python module '
                    'may be an easier workaround if newer rar is not readily '
                    'available.'.format(name),
                    info={'error': output}
                )
        return dirs, files, []

    cached = __salt__['cp.cache_file'](name, saltenv, source_hash=source_hash)
    if not cached:
        raise CommandExecutionError('Failed to cache {0}'.format(name))

    try:
        if strip_components:
            try:
                int(strip_components)
            except ValueError:
                strip_components = -1

            if strip_components <= 0:
                raise CommandExecutionError(
                    '\'strip_components\' must be a positive integer'
                )

        parsed = _urlparse(name)
        path = parsed.path or parsed.netloc

        def _unsupported_format(archive_format):
            '''
            Raise the proper exception message for the given archive format.
            '''
            if archive_format is None:
                raise CommandExecutionError(
                    'Unable to guess archive format, please pass an '
                    '\'archive_format\' argument.'
                )
            raise CommandExecutionError(
                'Unsupported archive format \'{0}\''.format(archive_format)
            )

        if not archive_format:
            guessed_format = salt.utils.files.guess_archive_type(path)
            if guessed_format is None:
                _unsupported_format(archive_format)
            archive_format = guessed_format

        func = locals().get('_list_' + archive_format)
        if not hasattr(func, '__call__'):
            _unsupported_format(archive_format)

        args = (options,) if archive_format == 'tar' else ()
        try:
            dirs, files, links = func(name, cached, *args)
        except (IOError, OSError) as exc:
            raise CommandExecutionError(
                'Failed to list contents of {0}: {1}'.format(
                    name, exc.__str__()
                )
            )
        except CommandExecutionError as exc:
            raise
        except Exception as exc:
            raise CommandExecutionError(
                'Uncaught exception \'{0}\' when listing contents of {1}'
                .format(exc, name)
            )

        if clean:
            try:
                os.remove(cached)
                log.debug('Cleaned cached archive %s', cached)
            except OSError as exc:
                if exc.errno != errno.ENOENT:
                    log.warning(
                        'Failed to clean cached archive %s: %s',
                        cached, exc.__str__()
                    )

        if strip_components:
            for item in (dirs, files, links):
                for index, path in enumerate(item):
                    try:
                        # Strip off the specified number of directory
                        # boundaries, and grab what comes after the last
                        # stripped path separator.
                        item[index] = item[index].split(
                            os.sep, strip_components)[strip_components]
                    except IndexError:
                        # Path is excluded by strip_components because it is not
                        # deep enough. Set this to an empty string so it can
                        # be removed in the generator expression below.
                        item[index] = ''

                # Remove all paths which were excluded
                item[:] = (x for x in item if x)
                item.sort()

        if verbose:
            ret = {'dirs': sorted(dirs),
                   'files': sorted(files),
                   'links': sorted(links)}
            ret['top_level_dirs'] = [x for x in ret['dirs']
                                     if x.count('/') == 1]
            ret['top_level_files'] = [x for x in ret['files']
                                      if x.count('/') == 0]
            ret['top_level_links'] = [x for x in ret['links']
                                      if x.count('/') == 0]
        else:
            ret = sorted(dirs + files + links)
        return ret

    except CommandExecutionError as exc:
        # Reraise with cache path in the error so that the user can examine the
        # cached archive for troubleshooting purposes.
        info = exc.info or {}
        info['archive location'] = cached
        raise CommandExecutionError(exc.error, info=info)