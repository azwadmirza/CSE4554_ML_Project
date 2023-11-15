    def url_replacer(self, src, dst, lang=None, url_type=None):
        """URL mangler.

        * Replaces link:// URLs with real links
        * Makes dst relative to src
        * Leaves fragments unchanged
        * Leaves full URLs unchanged
        * Avoids empty links

        src is the URL where this link is used
        dst is the link to be mangled
        lang is used for language-sensitive URLs in link://
        url_type is used to determine final link appearance, defaulting to URL_TYPE from config
        """
        parsed_src = urlsplit(src)
        src_elems = parsed_src.path.split('/')[1:]
        dst_url = urlparse(dst)
        if lang is None:
            lang = self.default_lang
        if url_type is None:
            url_type = self.config.get('URL_TYPE')

        if dst_url.scheme and dst_url.scheme not in ['http', 'https', 'link']:
            return dst

        # Refuse to replace links that are full URLs.
        if dst_url.netloc:
            if dst_url.scheme == 'link':  # Magic link
                dst = self.link(dst_url.netloc, dst_url.path.lstrip('/'), lang)
            # Assuming the site is served over one of these, and
            # since those are the only URLs we want to rewrite...
            else:
                if '%' in dst_url.netloc:
                    # convert lxml percent-encoded garbage to punycode
                    nl = unquote(dst_url.netloc)
                    try:
                        nl = nl.decode('utf-8')
                    except AttributeError:
                        # python 3: already unicode
                        pass
                    nl = nl.encode('idna')

                    dst = urlunsplit((dst_url.scheme,
                                      nl,
                                      dst_url.path,
                                      dst_url.query,
                                      dst_url.fragment))
                return dst
        elif dst_url.scheme == 'link':  # Magic absolute path link:
            dst = dst_url.path
            return dst

        # Refuse to replace links that consist of a fragment only
        if ((not dst_url.scheme) and (not dst_url.netloc) and
                (not dst_url.path) and (not dst_url.params) and
                (not dst_url.query) and dst_url.fragment):
            return dst

        # Normalize
        dst = urljoin(src, dst)

        # Avoid empty links.
        if src == dst:
            if url_type == 'absolute':
                dst = urljoin(self.config['BASE_URL'], dst.lstrip('/'))
                return dst
            elif url_type == 'full_path':
                dst = urljoin(self.config['BASE_URL'], dst.lstrip('/'))
                return urlparse(dst).path
            else:
                return "#"

        # Check that link can be made relative, otherwise return dest
        parsed_dst = urlsplit(dst)
        if parsed_src[:2] != parsed_dst[:2]:
            if url_type == 'absolute':
                dst = urljoin(self.config['BASE_URL'], dst)
            return dst

        if url_type in ('full_path', 'absolute'):
            dst = urljoin(self.config['BASE_URL'], dst.lstrip('/'))
            if url_type == 'full_path':
                parsed = urlparse(urljoin(self.config['BASE_URL'], dst.lstrip('/')))
                if parsed.fragment:
                    dst = '{0}#{1}'.format(parsed.path, parsed.fragment)
                else:
                    dst = parsed.path
            return dst

        # Now both paths are on the same site and absolute
        dst_elems = parsed_dst.path.split('/')[1:]

        i = 0
        for (i, s), d in zip(enumerate(src_elems), dst_elems):
            if s != d:
                break
        # Now i is the longest common prefix
        result = '/'.join(['..'] * (len(src_elems) - i - 1) + dst_elems[i:])

        if not result:
            result = "."

        # Don't forget the query part of the link
        if parsed_dst.query:
            result += "?" + parsed_dst.query

        # Don't forget the fragment (anchor) part of the link
        if parsed_dst.fragment:
            result += "#" + parsed_dst.fragment

        assert result, (src, dst, i, src_elems, dst_elems)

        return result