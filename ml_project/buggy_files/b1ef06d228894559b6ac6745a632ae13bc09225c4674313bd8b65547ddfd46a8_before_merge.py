    def run(self):
        if getattr(self.distribution, 'salt_download_windows_dlls', None) is None:
            print('This command is not meant to be called on it\'s own')
            exit(1)
        import platform
        from pip.utils.logging import indent_log
        platform_bits, _ = platform.architecture()
        url = 'https://repo.saltstack.com/windows/dependencies/{bits}/{fname}.dll'
        dest = os.path.join(os.path.dirname(sys.executable), '{fname}.dll')
        with indent_log():
            for fname in ('libeay32', 'ssleay32', 'libsodium', 'msvcr120'):
                # See if the library is already on the system
                if find_library(fname):
                    continue
                furl = url.format(bits=platform_bits[:2], fname=fname)
                fdest = dest.format(fname=fname)
                if not os.path.exists(fdest):
                    log.info('Downloading {0}.dll to {1} from {2}'.format(fname, fdest, furl))
                    try:
                        import requests
                        from contextlib import closing
                        with closing(requests.get(furl, stream=True)) as req:
                            if req.status_code == 200:
                                with open(fdest, 'wb') as wfh:
                                    for chunk in req.iter_content(chunk_size=4096):
                                        if chunk:  # filter out keep-alive new chunks
                                            wfh.write(chunk)
                                            wfh.flush()
                            else:
                                log.error(
                                    'Failed to download {0}.dll to {1} from {2}'.format(
                                        fname, fdest, furl
                                    )
                                )
                    except ImportError:
                        req = urlopen(furl)

                        if req.getcode() == 200:
                            with open(fdest, 'wb') as wfh:
                                if IS_PY3:
                                    while True:
                                        chunk = req.read(4096)
                                        if len(chunk) == 0:
                                            break;
                                        wfh.write(chunk)
                                        wfh.flush()
                                else:
                                    while True:
                                        for chunk in req.read(4096):
                                            if not chunk:
                                                break
                                            wfh.write(chunk)
                                            wfh.flush()
                        else:
                            log.error(
                                'Failed to download {0}.dll to {1} from {2}'.format(
                                    fname, fdest, furl
                                )
                            )