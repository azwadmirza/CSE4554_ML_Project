    def get_url(self, url, dest, makedirs=False, saltenv='base', env=None, no_cache=False):
        '''
        Get a single file from a URL.
        '''
        if env is not None:
            salt.utils.warn_until(
                'Boron',
                'Passing a salt environment should be done using \'saltenv\' '
                'not \'env\'. This functionality will be removed in Salt '
                'Boron.'
            )
            # Backwards compatibility
            saltenv = env

        url_data = urlparse(url)

        if url_data.scheme in ('file', ''):
            # Local filesystem
            if not os.path.isabs(url_data.path):
                raise CommandExecutionError(
                    'Path {0!r} is not absolute'.format(url_data.path)
                )
            return url_data.path

        if url_data.scheme == 'salt':
            return self.get_file(url, dest, makedirs, saltenv)
        if dest:
            destdir = os.path.dirname(dest)
            if not os.path.isdir(destdir):
                if makedirs:
                    os.makedirs(destdir)
                else:
                    return ''
        elif not no_cache:
            dest = self._extrn_path(url, saltenv)
            destdir = os.path.dirname(dest)
            if not os.path.isdir(destdir):
                os.makedirs(destdir)

        if url_data.scheme == 's3':
            try:
                salt.utils.s3.query(method='GET',
                                    bucket=url_data.netloc,
                                    path=url_data.path[1:],
                                    return_bin=False,
                                    local_file=dest,
                                    action=None,
                                    key=self.opts.get('s3.key', None),
                                    keyid=self.opts.get('s3.keyid', None),
                                    service_url=self.opts.get('s3.service_url',
                                                              None),
                                    verify_ssl=self.opts.get('s3.verify_ssl',
                                                              True),
                                    location=self.opts.get('s3.location',
                                                              None))
                return dest
            except Exception:
                raise MinionError('Could not fetch from {0}'.format(url))
        if url_data.scheme == 'ftp':
            try:
                ftp = ftplib.FTP(url_data.hostname)
                ftp.login()
                with salt.utils.fopen(dest, 'wb') as fp_:
                    ftp.retrbinary('RETR {0}'.format(url_data.path), fp_.write)
                return dest
            except Exception as exc:
                raise MinionError('Could not retrieve {0} from FTP server. Exception: {1}'.format(url, exc))

        if url_data.scheme == 'swift':
            try:
                swift_conn = SaltSwift(self.opts.get('keystone.user', None),
                                       self.opts.get('keystone.tenant', None),
                                       self.opts.get('keystone.auth_url', None),
                                       self.opts.get('keystone.password', None))
                swift_conn.get_object(url_data.netloc,
                                      url_data.path[1:],
                                      dest)
                return dest
            except Exception:
                raise MinionError('Could not fetch from {0}'.format(url))

        get_kwargs = {}
        if url_data.username is not None \
                and url_data.scheme in ('http', 'https'):
            _, netloc = url_data.netloc.split('@', 1)
            fixed_url = urlunparse(
                (url_data.scheme, netloc, url_data.path,
                 url_data.params, url_data.query, url_data.fragment))
            get_kwargs['auth'] = (url_data.username, url_data.password)
        else:
            fixed_url = url

        destfp = None
        try:
            query = salt.utils.http.query(
                fixed_url,
                stream=True,
                username=url_data.username,
                password=url_data.password,
                **get_kwargs
            )
            if 'handle' not in query:
                raise MinionError('Error: {0}'.format(query['error']))
            if no_cache:
                return query['body']
            else:
                dest_tmp = "{0}.part".format(dest)
                with salt.utils.fopen(dest_tmp, 'wb') as destfp:
                    destfp.write(query['body'])
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