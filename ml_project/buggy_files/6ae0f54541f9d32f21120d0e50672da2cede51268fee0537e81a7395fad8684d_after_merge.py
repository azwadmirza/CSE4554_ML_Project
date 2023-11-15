    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = []
        # hacky way to get the underlying lxml parsed document
        for el, attr, attr_val in self._iter_links(selector._root):
            if self.scan_tag(el.tag) and self.scan_attr(attr):
                # pseudo _root.make_links_absolute(base_url)
                attr_val = urljoin(base_url, attr_val)
                url = self.process_attr(attr_val)
                if url is None:
                    continue
                if isinstance(url, unicode):
                    url = url.encode(response_encoding)
                # to fix relative links after process_value
                url = urljoin(response_url, url)
                link = Link(url, _collect_string_content(el) or u'',
                    nofollow=True if el.get('rel') == 'nofollow' else False)
                links.append(link)

        return unique_list(links, key=lambda link: link.url) \
                if self.unique else links