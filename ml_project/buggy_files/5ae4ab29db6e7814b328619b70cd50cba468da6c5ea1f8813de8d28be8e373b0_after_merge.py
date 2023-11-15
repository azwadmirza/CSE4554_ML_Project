    def import_postpage_item(self, item, wordpress_namespace, out_folder=None, attachments=None):
        """Take an item from the feed and creates a post file."""
        if out_folder is None:
            out_folder = 'posts'

        title = get_text_tag(item, 'title', 'NO TITLE')
        # link is something like http://foo.com/2012/09/01/hello-world/
        # So, take the path, utils.slugify it, and that's our slug
        link = get_text_tag(item, 'link', None)
        parsed = urlparse(link)
        path = unquote(parsed.path.strip('/'))

        try:
            if isinstance(path, utils.bytes_str):
                path = path.decode('utf8', 'replace')
            else:
                path = path
        except AttributeError:
            pass

        # Cut out the base directory.
        if path.startswith(self.base_dir.strip('/')):
            path = path.replace(self.base_dir.strip('/'), '', 1)

        pathlist = path.split('/')
        if parsed.query:  # if there are no nice URLs and query strings are used
            out_folder = os.path.join(*([out_folder] + pathlist))
            slug = get_text_tag(
                item, '{{{0}}}post_name'.format(wordpress_namespace), None)
            if not slug:  # it *may* happen
                slug = get_text_tag(
                    item, '{{{0}}}post_id'.format(wordpress_namespace), None)
            if not slug:  # should never happen
                LOGGER.error("Error converting post:", title)
                return False
        else:
            if len(pathlist) > 1:
                out_folder = os.path.join(*([out_folder] + pathlist[:-1]))
            slug = utils.slugify(pathlist[-1])

        description = get_text_tag(item, 'description', '')
        post_date = get_text_tag(
            item, '{{{0}}}post_date'.format(wordpress_namespace), None)
        try:
            dt = utils.to_datetime(post_date)
        except ValueError:
            dt = datetime.datetime(1970, 1, 1, 0, 0, 0)
            LOGGER.error('Malformed date "{0}" in "{1}" [{2}], assuming 1970-01-01 00:00:00 instead.'.format(post_date, title, slug))
            post_date = dt.strftime('%Y-%m-%d %H:%M:%S')

        if dt.tzinfo and self.timezone is None:
            self.timezone = utils.get_tzname(dt)
        status = get_text_tag(
            item, '{{{0}}}status'.format(wordpress_namespace), 'publish')
        content = get_text_tag(
            item, '{http://purl.org/rss/1.0/modules/content/}encoded', '')
        excerpt = get_text_tag(
            item, '{http://wordpress.org/export/1.2/excerpt/}encoded', None)

        if excerpt is not None:
            if len(excerpt) == 0:
                excerpt = None

        tags = []
        categories = []
        if status == 'trash':
            LOGGER.warn('Trashed post "{0}" will not be imported.'.format(title))
            return False
        elif status == 'private':
            tags.append('private')
            is_draft = False
            is_private = True
        elif status != 'publish':
            tags.append('draft')
            is_draft = True
            is_private = False
        else:
            is_draft = False
            is_private = False

        for tag in item.findall('category'):
            text = tag.text
            type = 'category'
            if 'domain' in tag.attrib:
                type = tag.attrib['domain']
            if text == 'Uncategorized' and type == 'category':
                continue
            self.all_tags.add(text)
            if type == 'category':
                categories.append(text)
            else:
                tags.append(text)

        if '$latex' in content:
            tags.append('mathjax')

        # Find post format if it's there
        post_format = 'wp'
        format_tag = [x for x in item.findall('*//{%s}meta_key' % wordpress_namespace) if x.text == '_tc_post_format']
        if format_tag:
            post_format = format_tag[0].getparent().find('{%s}meta_value' % wordpress_namespace).text
            if post_format == 'wpautop':
                post_format = 'wp'

        if is_draft and self.exclude_drafts:
            LOGGER.notice('Draft "{0}" will not be imported.'.format(title))
            return False
        elif is_private and self.exclude_privates:
            LOGGER.notice('Private post "{0}" will not be imported.'.format(title))
            return False
        elif content.strip() or self.import_empty_items:
            # If no content is found, no files are written.
            self.url_map[link] = (self.context['SITE_URL'] +
                                  out_folder.rstrip('/') + '/' + slug +
                                  '.html').replace(os.sep, '/')
            if hasattr(self, "separate_qtranslate_content") \
               and self.separate_qtranslate_content:
                content_translations = separate_qtranslate_content(content)
            else:
                content_translations = {"": content}
            default_language = self.context["DEFAULT_LANG"]
            for lang, content in content_translations.items():
                try:
                    content, extension, rewrite_html = self.transform_content(content, post_format, attachments)
                except:
                    LOGGER.error(('Cannot interpret post "{0}" (language {1}) with post ' +
                                  'format {2}!').format(os.path.join(out_folder, slug), lang, post_format))
                    return False
                if lang:
                    out_meta_filename = slug + '.meta'
                    if lang == default_language:
                        out_content_filename = slug + '.' + extension
                    else:
                        out_content_filename \
                            = utils.get_translation_candidate(self.context,
                                                              slug + "." + extension, lang)
                        self.extra_languages.add(lang)
                    meta_slug = slug
                else:
                    out_meta_filename = slug + '.meta'
                    out_content_filename = slug + '.' + extension
                    meta_slug = slug
                tags, other_meta = self._create_metadata(status, excerpt, tags, categories,
                                                         post_name=os.path.join(out_folder, slug))
                self.write_metadata(os.path.join(self.output_folder, out_folder,
                                                 out_meta_filename),
                                    title, meta_slug, post_date, description, tags, **other_meta)
                self.write_content(
                    os.path.join(self.output_folder,
                                 out_folder, out_content_filename),
                    content,
                    rewrite_html)

            if self.export_comments:
                comments = []
                for tag in item.findall('{{{0}}}comment'.format(wordpress_namespace)):
                    comment = self._extract_comment(tag, wordpress_namespace)
                    if comment is not None:
                        comments.append(comment)

                for comment in comments:
                    comment_filename = "{0}.{1}.wpcomment".format(slug, comment['id'])
                    self._write_comment(os.path.join(self.output_folder, out_folder, comment_filename), comment)

            return (out_folder, slug)
        else:
            LOGGER.warn(('Not going to import "{0}" because it seems to contain'
                         ' no content.').format(title))
            return False