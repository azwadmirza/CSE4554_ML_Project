    def get_url(self, url, dest, makedirs=False, saltenv='base',
                no_cache=False, cachedir=None, source_hash=None):
        '''
        Get a single file from a URL.
        '''
        url_data = urlparse(url)
        url_scheme = url_data.scheme
        url_path = os.path.join(
                url_data.netloc, url_data.path).rstrip(os.sep)

        # If dest is a directory, rewrite dest with filename
        if dest is not None \
                and (os.path.isdir(dest) or dest.endswith(('/', '\\'))):
            if url_data.query or len(url_data.path) > 1 and not url_data.path.endswith('/'):
                strpath = url.split('/')[-1]
            else:
                strpath = 'index.html'

            if salt.utils.platform.is_windows():
                strpath = salt.utils.path.sanitize_win_path(strpath)

            dest = os.path.join(dest, strpath)

        if url_scheme and url_scheme.lower() in string.ascii_lowercase:
            url_path = ':'.join((url_scheme, url_path))
            url_scheme = 'file'

        if url_scheme in ('file', ''):
            # Local filesystem
            if not os.path.isabs(url_path):
                raise CommandExecutionError(
                    'Path \'{0}\' is not absolute'.format(url_path)
                )
            if dest is None:
                with salt.utils.files.fopen(url_path, 'rb') as fp_:
                    data = fp_.read()
                return data
            return url_path

        if url_scheme == 'salt':
            result = self.get_file(url, dest, makedirs, saltenv, cachedir=cachedir)
            if result and dest is None:
                with salt.utils.files.fopen(result, 'rb') as fp_:
                    data = fp_.read()
                return data
            return result

        if dest:
            destdir = os.path.dirname(dest)
            if not os.path.isdir(destdir):
                if makedirs:
                    os.makedirs(destdir)
                else:
                    return ''
        elif not no_cache:
            dest = self._extrn_path(url, saltenv, cachedir=cachedir)
            if source_hash is not None:
                try:
                    source_hash = source_hash.split('=')[-1]
                    form = salt.utils.files.HASHES_REVMAP[len(source_hash)]
                    if salt.utils.hashutils.get_hash(dest, form) == source_hash:
                        log.debug(
                            'Cached copy of %s (%s) matches source_hash %s, '
                            'skipping download', url, dest, source_hash
                        )
                        return dest
                except (AttributeError, KeyError, IOError, OSError):
                    pass
            destdir = os.path.dirname(dest)
            if not os.path.isdir(destdir):
                os.makedirs(destdir)

        if url_data.scheme == 's3':
            try:
                def s3_opt(key, default=None):
                    '''
                    Get value of s3.<key> from Minion config or from Pillar
                    '''
                    if 's3.' + key in self.opts:
                        return self.opts['s3.' + key]
                    try:
                        return self.opts['pillar']['s3'][key]
                    except (KeyError, TypeError):
                        return default
                self.utils['s3.query'](method='GET',
                                       bucket=url_data.netloc,
                                       path=url_data.path[1:],
                                       return_bin=False,
                                       local_file=dest,
                                       action=None,
                                       key=s3_opt('key'),
                                       keyid=s3_opt('keyid'),
                                       service_url=s3_opt('service_url'),
                                       verify_ssl=s3_opt('verify_ssl', True),
                                       location=s3_opt('location'),
                                       path_style=s3_opt('path_style', False),
                                       https_enable=s3_opt('https_enable', True))
                return dest
            except Exception as exc:  # pylint: disable=broad-except
                raise MinionError(
                    'Could not fetch from {0}. Exception: {1}'.format(url, exc)
                )
        if url_data.scheme == 'ftp':
            try:
                ftp = ftplib.FTP()
                ftp.connect(url_data.hostname, url_data.port)
                ftp.login(url_data.username, url_data.password)
                remote_file_path = url_data.path.lstrip('/')
                with salt.utils.files.fopen(dest, 'wb') as fp_:
                    ftp.retrbinary('RETR {0}'.format(remote_file_path), fp_.write)
                ftp.quit()
                return dest
            except Exception as exc:  # pylint: disable=broad-except
                raise MinionError('Could not retrieve {0} from FTP server. Exception: {1}'.format(url, exc))

        if url_data.scheme == 'swift':
            try:
                def swift_opt(key, default):
                    '''
                    Get value of <key> from Minion config or from Pillar
                    '''
                    if key in self.opts:
                        return self.opts[key]
                    try:
                        return self.opts['pillar'][key]
                    except (KeyError, TypeError):
                        return default

                swift_conn = SaltSwift(swift_opt('keystone.user', None),
                                       swift_opt('keystone.tenant', None),
                                       swift_opt('keystone.auth_url', None),
                                       swift_opt('keystone.password', None))

                swift_conn.get_object(url_data.netloc,
                                      url_data.path[1:],
                                      dest)
                return dest
            except Exception:  # pylint: disable=broad-except
                raise MinionError('Could not fetch from {0}'.format(url))

        get_kwargs = {}
        if url_data.username is not None \
                and url_data.scheme in ('http', 'https'):
            netloc = url_data.netloc
            at_sign_pos = netloc.rfind('@')
            if at_sign_pos != -1:
                netloc = netloc[at_sign_pos + 1:]
            fixed_url = urlunparse(
                (url_data.scheme, netloc, url_data.path,
                 url_data.params, url_data.query, url_data.fragment))
            get_kwargs['auth'] = (url_data.username, url_data.password)
        else:
            fixed_url = url

        destfp = None
        try:
            # Tornado calls streaming_callback on redirect response bodies.
            # But we need streaming to support fetching large files (> RAM
            # avail). Here we are working around this by disabling recording
            # the body for redirections. The issue is fixed in Tornado 4.3.0
            # so on_header callback could be removed when we'll deprecate
            # Tornado<4.3.0. See #27093 and #30431 for details.

            # Use list here to make it writable inside the on_header callback.
            # Simple bool doesn't work here: on_header creates a new local
            # variable instead. This could be avoided in Py3 with 'nonlocal'
            # statement. There is no Py2 alternative for this.
            #
            # write_body[0] is used by the on_chunk callback to tell it whether
            #   or not we need to write the body of the request to disk. For
            #   30x redirects we set this to False because we don't want to
            #   write the contents to disk, as we will need to wait until we
            #   get to the redirected URL.
            #
            # write_body[1] will contain a tornado.httputil.HTTPHeaders
            #   instance that we will use to parse each header line. We
            #   initialize this to False, and after we parse the status line we
            #   will replace it with the HTTPHeaders instance. If/when we have
            #   found the encoding used in the request, we set this value to
            #   False to signify that we are done parsing.
            #
            # write_body[2] is where the encoding will be stored
            write_body = [None, False, None]

            def on_header(hdr):
                if write_body[1] is not False and write_body[2] is None:
                    if not hdr.strip() and 'Content-Type' not in write_body[1]:
                        # If write_body[0] is True, then we are not following a
                        # redirect (initial response was a 200 OK). So there is
                        # no need to reset write_body[0].
                        if write_body[0] is not True:
                            # We are following a redirect, so we need to reset
                            # write_body[0] so that we properly follow it.
                            write_body[0] = None
                        # We don't need the HTTPHeaders object anymore
                        write_body[1] = False
                        return
                    # Try to find out what content type encoding is used if
                    # this is a text file
                    write_body[1].parse_line(hdr)  # pylint: disable=no-member
                    if 'Content-Type' in write_body[1]:
                        content_type = write_body[1].get('Content-Type')  # pylint: disable=no-member
                        if not content_type.startswith('text'):
                            write_body[1] = write_body[2] = False
                        else:
                            encoding = 'utf-8'
                            fields = content_type.split(';')
                            for field in fields:
                                if 'encoding' in field:
                                    encoding = field.split('encoding=')[-1]
                            write_body[2] = encoding
                            # We have found our encoding. Stop processing headers.
                            write_body[1] = False

                        # If write_body[0] is False, this means that this
                        # header is a 30x redirect, so we need to reset
                        # write_body[0] to None so that we parse the HTTP
                        # status code from the redirect target. Additionally,
                        # we need to reset write_body[2] so that we inspect the
                        # headers for the Content-Type of the URL we're
                        # following.
                        if write_body[0] is write_body[1] is False:
                            write_body[0] = write_body[2] = None

                # Check the status line of the HTTP request
                if write_body[0] is None:
                    try:
                        hdr = parse_response_start_line(hdr)
                    except HTTPInputError:
                        # Not the first line, do nothing
                        return
                    write_body[0] = hdr.code not in [301, 302, 303, 307]
                    write_body[1] = HTTPHeaders()

            if no_cache:
                result = []

                def on_chunk(chunk):
                    if write_body[0]:
                        if write_body[2]:
                            chunk = chunk.decode(write_body[2])
                        result.append(chunk)
            else:
                dest_tmp = u"{0}.part".format(dest)
                # We need an open filehandle to use in the on_chunk callback,
                # that's why we're not using a with clause here.
                destfp = salt.utils.files.fopen(dest_tmp, 'wb')  # pylint: disable=resource-leakage

                def on_chunk(chunk):
                    if write_body[0]:
                        destfp.write(chunk)

            query = salt.utils.http.query(
                fixed_url,
                stream=True,
                streaming_callback=on_chunk,
                header_callback=on_header,
                username=url_data.username,
                password=url_data.password,
                opts=self.opts,
                **get_kwargs
            )
            if 'handle' not in query:
                raise MinionError('Error: {0} reading {1}'.format(query['error'], url))
            if no_cache:
                if write_body[2]:
                    return ''.join(result)
                return b''.join(result)
            else:
                destfp.close()
                destfp = None
                salt.utils.files.rename(dest_tmp, dest)
                return dest
        except HTTPError as exc:
            raise MinionError('HTTP error {0} reading {1}: {3}'.format(
                exc.code,
                url,
                *BaseHTTPServer.BaseHTTPRequestHandler.responses[exc.code]))
        except URLError as exc:
            raise MinionError('Error reading {0}: {1}'.format(url, exc.reason))
        finally:
            if destfp is not None:
                destfp.close()