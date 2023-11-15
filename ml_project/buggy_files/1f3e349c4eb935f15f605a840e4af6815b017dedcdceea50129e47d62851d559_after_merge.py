    def text(self, lang=None, teaser_only=False, strip_html=False, show_read_more_link=True,
             feed_read_more_link=False, feed_links_append_query=None):
        """Read the post file for that language and return its contents.

        teaser_only=True breaks at the teaser marker and returns only the teaser.
        strip_html=True removes HTML tags
        show_read_more_link=False does not add the Read more... link
        feed_read_more_link=True uses FEED_READ_MORE_LINK instead of INDEX_READ_MORE_LINK
        lang=None uses the last used to set locale

        All links in the returned HTML will be relative.
        The HTML returned is a bare fragment, not a full document.
        """
        if lang is None:
            lang = nikola.utils.LocaleBorg().current_lang
        file_name = self._translated_file_path(lang)

        # Yes, we compile it and screw it.
        # This may be controversial, but the user (or someone) is asking for the post text
        # and the post should not just refuse to give it.
        if not os.path.isfile(file_name):
            self.compile(lang)

        with io.open(file_name, "r", encoding="utf8") as post_file:
            data = post_file.read().strip()

        if self.compiler.extension() == '.php':
            return data
        try:
            document = lxml.html.fragment_fromstring(data, "body")
        except lxml.etree.ParserError as e:
            # if we don't catch this, it breaks later (Issue #374)
            if str(e) == "Document is empty":
                return ""
            # let other errors raise
            raise(e)
        base_url = self.permalink(lang=lang)
        document.make_links_absolute(base_url)

        if self.hyphenate:
            hyphenate(document, lang)

        try:
            data = lxml.html.tostring(document.body, encoding='unicode')
        except:
            data = lxml.html.tostring(document, encoding='unicode')

        if teaser_only:
            teaser_regexp = self.config.get('TEASER_REGEXP', TEASER_REGEXP)
            teaser = teaser_regexp.split(data)[0]
            if teaser != data:
                if not strip_html and show_read_more_link:
                    if teaser_regexp.search(data).groups()[-1]:
                        teaser_text = teaser_regexp.search(data).groups()[-1]
                    else:
                        teaser_text = self.messages[lang]["Read more"]
                    l = self.config['FEED_READ_MORE_LINK'](lang) if feed_read_more_link else self.config['INDEX_READ_MORE_LINK'](lang)
                    teaser += l.format(
                        link=self.permalink(lang, query=feed_links_append_query),
                        read_more=teaser_text,
                        min_remaining_read=self.messages[lang]["%d min remaining to read"] % (self.remaining_reading_time),
                        reading_time=self.reading_time,
                        remaining_reading_time=self.remaining_reading_time,
                        paragraph_count=self.paragraph_count,
                        remaining_paragraph_count=self.remaining_paragraph_count)
                # This closes all open tags and sanitizes the broken HTML
                document = lxml.html.fromstring(teaser)
                try:
                    data = lxml.html.tostring(document.body, encoding='unicode')
                except IndexError:
                    data = lxml.html.tostring(document, encoding='unicode')

        if data and strip_html:
            try:
                # Not all posts have a body. For example, you may have a page statically defined in the template that does not take content as input.
                content = lxml.html.fromstring(data)
                data = content.text_content().strip()  # No whitespace wanted.
            except (lxml.etree.ParserError, ValueError):
                data = ""
        elif data:
            if self.demote_headers:
                # see above
                try:
                    document = lxml.html.fromstring(data)
                    demote_headers(document, self.demote_headers)
                    data = lxml.html.tostring(document.body, encoding='unicode')
                except (lxml.etree.ParserError, IndexError):
                    data = lxml.html.tostring(document, encoding='unicode')

        return data