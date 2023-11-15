    def extendMarkdown(self, md, md_globals):
        # type: (markdown.Markdown, Dict[str, Any]) -> None
        del md.preprocessors['reference']

        for k in ('image_link', 'image_reference', 'automail',
                  'autolink', 'link', 'reference', 'short_reference',
                  'escape', 'strong_em', 'emphasis', 'emphasis2',
                  'linebreak', 'strong'):
            del md.inlinePatterns[k]
        try:
            # linebreak2 was removed upstream in version 3.2.1, so
            # don't throw an error if it is not there
            del md.inlinePatterns['linebreak2']
        except Exception:
            pass

        md.preprocessors.add("custom_text_notifications", AlertWordsNotificationProcessor(md), "_end")

        # Custom bold syntax: **foo** but not __foo__
        md.inlinePatterns.add('strong',
            markdown.inlinepatterns.SimpleTagPattern(r'(\*\*)([^\n]+?)\2', 'strong'),
            '>not_strong')

        for k in ('hashheader', 'setextheader', 'olist', 'ulist'):
            del md.parser.blockprocessors[k]

        md.parser.blockprocessors.add('ulist', UListProcessor(md.parser), '>hr')

        # Note that !gravatar syntax should be deprecated long term.
        md.inlinePatterns.add('avatar', Avatar(r'!avatar\((?P<email>[^)]*)\)'), '>backtick')
        md.inlinePatterns.add('gravatar', Avatar(r'!gravatar\((?P<email>[^)]*)\)'), '>backtick')

        md.inlinePatterns.add('stream_subscribe_button',
            StreamSubscribeButton(r'!_stream_subscribe_button\((?P<stream_name>(?:[^)\\]|\\\)|\\)*)\)'), '>backtick')
        md.inlinePatterns.add(
            'modal_link',
            ModalLink(r'!modal_link\((?P<relative_url>[^)]*), (?P<text>[^)]*)\)'),
            '>backtick')
        md.inlinePatterns.add('usermention', UserMentionPattern(mention.find_mentions), '>backtick')
        md.inlinePatterns.add('emoji', Emoji(r'(?<!\w)(?P<syntax>:[^:\s]+:)(?!\w)'), '_end')
        md.inlinePatterns.add('unicodeemoji', UnicodeEmoji(
            u'(?<!\\w)(?P<syntax>[\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF])(?!\\w)'),
            '_end')

        md.inlinePatterns.add('link', AtomicLinkPattern(markdown.inlinepatterns.LINK_RE, md), '>backtick')

        for (pattern, format_string) in self.getConfig("realm_filters"):
            md.inlinePatterns.add('realm_filters/%s' % (pattern,),
                                  RealmFilterPattern(pattern, format_string), '>link')

        # A link starts at a word boundary, and ends at space, punctuation, or end-of-input.
        #
        # We detect a url either by the `https?://` or by building around the TLD.

        # In lieu of having a recursive regex (which python doesn't support) to match
        # arbitrary numbers of nested matching parenthesis, we manually build a regexp that
        # can match up to six
        # The inner_paren_contents chunk matches the innermore non-parenthesis-holding text,
        # and the paren_group matches text with, optionally, a matching set of parens
        inner_paren_contents = r"[^\s()\"]*"
        paren_group = r"""
                        [^\s()\"]*?            # Containing characters that won't end the URL
                        (?: \( %s \)           # and more characters in matched parens
                            [^\s()\"]*?        # followed by more characters
                        )*                     # zero-or-more sets of paired parens
                       """
        nested_paren_chunk = paren_group
        for i in range(6):
            nested_paren_chunk = nested_paren_chunk % (paren_group,)
        nested_paren_chunk = nested_paren_chunk % (inner_paren_contents,)
        tlds = '|'.join(list_of_tlds())
        link_regex = r"""
            (?<![^\s'"\(,:<])    # Start after whitespace or specified chars
                                 # (Double-negative lookbehind to allow start-of-string)
            (?P<url>             # Main group
                (?:(?:           # Domain part
                    https?://[\w.:@-]+?   # If it has a protocol, anything goes.
                   |(?:                   # Or, if not, be more strict to avoid false-positives
                        (?:[\w-]+\.)+     # One or more domain components, separated by dots
                        (?:%s)            # TLDs (filled in via format from tlds-alpha-by-domain.txt)
                    )
                )
                (?:/             # A path, beginning with /
                    %s           # zero-to-6 sets of paired parens
                )?)              # Path is optional
                | (?:[\w.-]+\@[\w.-]+\.[\w]+) # Email is separate, since it can't have a path
            )
            (?=                            # URL must be followed by (not included in group)
                [!:;\?\),\.\'\"\>]*         # Optional punctuation characters
                (?:\Z|\s)                  # followed by whitespace or end of string
            )
            """ % (tlds, nested_paren_chunk)
        md.inlinePatterns.add('autolink', AutoLink(link_regex), '>link')

        md.preprocessors.add('hanging_ulists',
                                 BugdownUListPreprocessor(md),
                                 "_begin")

        md.treeprocessors.add("inline_interesting_links", InlineInterestingLinkProcessor(md, self), "_end")

        if settings.CAMO_URI:
            md.treeprocessors.add("rewrite_to_https", InlineHttpsProcessor(md), "_end")

        if self.getConfig("realm") == "zephyr_mirror":
            # Disable almost all inline patterns for zephyr mirror
            # users' traffic that is mirrored.  Note that
            # inline_interesting_links is a treeprocessor and thus is
            # not removed
            for k in list(md.inlinePatterns.keys()):
                if k not in ["autolink"]:
                    del md.inlinePatterns[k]
            for k in list(md.treeprocessors.keys()):
                if k not in ["inline_interesting_links", "inline", "rewrite_to_https"]:
                    del md.treeprocessors[k]
            for k in list(md.preprocessors.keys()):
                if k not in ["custom_text_notifications"]:
                    del md.preprocessors[k]
            for k in list(md.parser.blockprocessors.keys()):
                if k not in ["paragraph"]:
                    del md.parser.blockprocessors[k]