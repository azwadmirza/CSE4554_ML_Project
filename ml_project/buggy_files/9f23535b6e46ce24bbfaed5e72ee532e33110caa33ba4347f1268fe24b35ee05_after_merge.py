    def get_page(cls, link, req, cache=None, skip_archives=True):
        url = link.url
        url = url.split('#', 1)[0]
        if cache.too_many_failures(url):
            return None

        # Check for VCS schemes that do not support lookup as web pages.
        from pip.vcs import VcsSupport
        for scheme in VcsSupport.schemes:
            if url.lower().startswith(scheme) and url[len(scheme)] in '+:':
                logger.debug('Cannot look at %(scheme)s URL %(link)s' % locals())
                return None

        if cache is not None:
            inst = cache.get_page(url)
            if inst is not None:
                return inst
        try:
            if skip_archives:
                if cache is not None:
                    if cache.is_archive(url):
                        return None
                filename = link.filename
                for bad_ext in ['.tar', '.tar.gz', '.tar.bz2', '.tgz', '.zip']:
                    if filename.endswith(bad_ext):
                        content_type = cls._get_content_type(url)
                        if content_type.lower().startswith('text/html'):
                            break
                        else:
                            logger.debug('Skipping page %s because of Content-Type: %s' % (link, content_type))
                            if cache is not None:
                                cache.set_is_archive(url)
                            return None
            logger.debug('Getting page %s' % url)

            # Tack index.html onto file:// URLs that point to directories
            (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
            if scheme == 'file' and os.path.isdir(url2pathname(path)):
                # add trailing slash if not present so urljoin doesn't trim final segment
                if not url.endswith('/'):
                    url += '/'
                url = urlparse.urljoin(url, 'index.html')
                logger.debug(' file: URL is directory, getting %s' % url)

            resp = urlopen(url)

            real_url = geturl(resp)
            headers = resp.info()
            contents = resp.read()
            encoding = headers.get('Content-Encoding', None)
            #XXX need to handle exceptions and add testing for this
            if encoding is not None:
                if encoding == 'gzip':
                    contents = gzip.GzipFile(fileobj=BytesIO(contents)).read()
                if encoding == 'deflate':
                    contents = zlib.decompress(contents)

            # The check for archives above only works if the url ends with
            #   something that looks like an archive. However that is not a
            #   requirement. For instance http://sourceforge.net/projects/docutils/files/docutils/0.8.1/docutils-0.8.1.tar.gz/download
            #   redirects to http://superb-dca3.dl.sourceforge.net/project/docutils/docutils/0.8.1/docutils-0.8.1.tar.gz
            #   Unless we issue a HEAD request on every url we cannot know
            #   ahead of time for sure if something is HTML or not. However we
            #   can check after we've downloaded it.
            content_type = headers.get('Content-Type', 'unknown')
            if not content_type.lower().startswith("text/html"):
                logger.debug('Skipping page %s because of Content-Type: %s' %
                                            (link, content_type))
                if cache is not None:
                    cache.set_is_archive(url)
                return None

            inst = cls(u(contents), real_url, headers, trusted=link.trusted)
        except (HTTPError, URLError, socket.timeout, socket.error, OSError, WindowsError):
            e = sys.exc_info()[1]
            desc = str(e)
            if isinstance(e, socket.timeout):
                log_meth = logger.info
                level =1
                desc = 'timed out'
            elif isinstance(e, URLError):
                #ssl/certificate error
                if hasattr(e, 'reason') and (isinstance(e.reason, ssl.SSLError) or isinstance(e.reason, CertificateError)):
                    desc = 'There was a problem confirming the ssl certificate: %s' % e
                    log_meth = logger.notify
                else:
                    log_meth = logger.info
                if hasattr(e, 'reason') and isinstance(e.reason, socket.timeout):
                    desc = 'timed out'
                    level = 1
                else:
                    level = 2
            elif isinstance(e, HTTPError) and e.code == 404:
                ## FIXME: notify?
                log_meth = logger.info
                level = 2
            else:
                log_meth = logger.info
                level = 1
            log_meth('Could not fetch URL %s: %s' % (link, desc))
            log_meth('Will skip URL %s when looking for download links for %s' % (link.url, req))
            if cache is not None:
                cache.add_page_failure(url, level)
            return None
        if cache is not None:
            cache.add_page([url, real_url], inst)
        return inst