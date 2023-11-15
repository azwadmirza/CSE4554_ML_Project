    def __init__(self, **config):
        """Initialize proper environment for running tasks."""
        # Register our own path handlers
        self.path_handlers = {
            'slug': self.slug_path,
            'post_path': self.post_path,
            'root': self.root_path,
            'filename': self.filename_path,
        }

        self.strict = False
        self.posts = []
        self.all_posts = []
        self.posts_per_year = defaultdict(list)
        self.posts_per_month = defaultdict(list)
        self.posts_per_tag = defaultdict(list)
        self.posts_per_category = defaultdict(list)
        self.tags_per_language = defaultdict(list)
        self.post_per_file = {}
        self.timeline = []
        self.pages = []
        self._scanned = False
        self._template_system = None
        self._THEMES = None
        self._MESSAGES = None
        self.filters = {}
        self.debug = DEBUG
        self.loghandlers = utils.STDERR_HANDLER  # TODO remove on v8
        self.colorful = config.pop('__colorful__', False)
        self.invariant = config.pop('__invariant__', False)
        self.quiet = config.pop('__quiet__', False)
        self._doit_config = config.pop('DOIT_CONFIG', {})
        self.original_cwd = config.pop('__cwd__', False)
        self.configuration_filename = config.pop('__configuration_filename__', False)
        self.configured = bool(config)
        self.injected_deps = defaultdict(list)
        self.shortcode_registry = {}

        self.rst_transforms = []
        self.template_hooks = {
            'extra_head': utils.TemplateHookRegistry('extra_head', self),
            'body_end': utils.TemplateHookRegistry('body_end', self),
            'page_header': utils.TemplateHookRegistry('page_header', self),
            'menu': utils.TemplateHookRegistry('menu', self),
            'menu_alt': utils.TemplateHookRegistry('menu_alt', self),
            'page_footer': utils.TemplateHookRegistry('page_footer', self),
        }

        # Maintain API
        utils.generic_rss_renderer = self.generic_rss_renderer

        # This is the default config
        self.config = {
            'ANNOTATIONS': False,
            'ARCHIVE_PATH': "",
            'ARCHIVE_FILENAME': "archive.html",
            'ARCHIVES_ARE_INDEXES': False,
            'AUTHOR_PATH': 'authors',
            'AUTHOR_PAGES_ARE_INDEXES': False,
            'AUTHOR_PAGES_DESCRIPTIONS': {},
            'AUTHORLIST_MINIMUM_POSTS': 1,
            'BLOG_AUTHOR': 'Default Author',
            'BLOG_TITLE': 'Default Title',
            'BLOG_DESCRIPTION': 'Default Description',
            'BODY_END': "",
            'CACHE_FOLDER': 'cache',
            'CATEGORIES_INDEX_PATH': '',
            'CATEGORY_PATH': None,  # None means: same as TAG_PATH
            'CATEGORY_PAGES_ARE_INDEXES': None,  # None means: same as TAG_PAGES_ARE_INDEXES
            'CATEGORY_PAGES_DESCRIPTIONS': {},
            'CATEGORY_PAGES_TITLES': {},
            'CATEGORY_PREFIX': 'cat_',
            'CATEGORY_ALLOW_HIERARCHIES': False,
            'CATEGORY_OUTPUT_FLAT_HIERARCHY': False,
            'CATEGORY_TRANSLATIONS': [],
            'CATEGORY_TRANSLATIONS_ADD_DEFAULTS': False,
            'CODE_COLOR_SCHEME': 'default',
            'COMMENT_SYSTEM': 'disqus',
            'COMMENTS_IN_GALLERIES': False,
            'COMMENTS_IN_PAGES': False,
            'COMPILERS': {
                "rest": ('.txt', '.rst'),
                "markdown": ('.md', '.mdown', '.markdown'),
                "textile": ('.textile',),
                "txt2tags": ('.t2t',),
                "bbcode": ('.bb',),
                "wiki": ('.wiki',),
                "ipynb": ('.ipynb',),
                "html": ('.html', '.htm')
            },
            'CONTENT_FOOTER': '',
            'CONTENT_FOOTER_FORMATS': {},
            'RSS_COPYRIGHT': '',
            'RSS_COPYRIGHT_PLAIN': '',
            'RSS_COPYRIGHT_FORMATS': {},
            'COPY_SOURCES': True,
            'CREATE_ARCHIVE_NAVIGATION': False,
            'CREATE_MONTHLY_ARCHIVE': False,
            'CREATE_SINGLE_ARCHIVE': False,
            'CREATE_FULL_ARCHIVES': False,
            'CREATE_DAILY_ARCHIVE': False,
            'DATE_FORMAT': '%Y-%m-%d %H:%M',
            'DISABLE_INDEXES_PLUGIN_INDEX_AND_ATOM_FEED': False,
            'DISABLE_INDEXES_PLUGIN_RSS_FEED': False,
            'JS_DATE_FORMAT': 'YYYY-MM-DD HH:mm',
            'DATE_FANCINESS': 0,
            'DEFAULT_LANG': "en",
            'DEPLOY_COMMANDS': {'default': []},
            'DISABLED_PLUGINS': [],
            'EXTRA_PLUGINS_DIRS': [],
            'EXTRA_THEMES_DIRS': [],
            'COMMENT_SYSTEM_ID': 'nikolademo',
            'ENABLE_AUTHOR_PAGES': True,
            'EXIF_WHITELIST': {},
            'EXTRA_HEAD_DATA': '',
            'FAVICONS': (),
            'FEED_LENGTH': 10,
            'FILE_METADATA_REGEXP': None,
            'ADDITIONAL_METADATA': {},
            'FILES_FOLDERS': {'files': ''},
            'FILTERS': {},
            'FORCE_ISO8601': False,
            'FRONT_INDEX_HEADER': '',
            'GALLERY_FOLDERS': {'galleries': 'galleries'},
            'GALLERY_SORT_BY_DATE': True,
            'GLOBAL_CONTEXT_FILLER': [],
            'GZIP_COMMAND': None,
            'GZIP_FILES': False,
            'GZIP_EXTENSIONS': ('.txt', '.htm', '.html', '.css', '.js', '.json', '.xml'),
            'HIDDEN_AUTHORS': [],
            'HIDDEN_TAGS': [],
            'HIDE_REST_DOCINFO': False,
            'HIDDEN_CATEGORIES': [],
            'HYPHENATE': False,
            'IMAGE_FOLDERS': {'images': ''},
            'INDEX_DISPLAY_POST_COUNT': 10,
            'INDEX_FILE': 'index.html',
            'INDEX_TEASERS': False,
            'IMAGE_THUMBNAIL_SIZE': 400,
            'IMAGE_THUMBNAIL_FORMAT': '{name}.thumbnail{ext}',
            'INDEXES_TITLE': "",
            'INDEXES_PAGES': "",
            'INDEXES_PAGES_MAIN': False,
            'INDEXES_PRETTY_PAGE_URL': False,
            'INDEXES_STATIC': True,
            'INDEX_PATH': '',
            'IPYNB_CONFIG': {},
            'KATEX_AUTO_RENDER': '',
            'LESS_COMPILER': 'lessc',
            'LESS_OPTIONS': [],
            'LICENSE': '',
            'LINK_CHECK_WHITELIST': [],
            'LISTINGS_FOLDERS': {'listings': 'listings'},
            'LOGO_URL': '',
            'NAVIGATION_LINKS': {},
            'MARKDOWN_EXTENSIONS': ['fenced_code', 'codehilite'],  # FIXME: Add 'extras' in v8
            'MAX_IMAGE_SIZE': 1280,
            'MATHJAX_CONFIG': '',
            'METADATA_FORMAT': 'nikola',
            'METADATA_MAPPING': {},
            'NEW_POST_DATE_PATH': False,
            'NEW_POST_DATE_PATH_FORMAT': '%Y/%m/%d',
            'OLD_THEME_SUPPORT': True,
            'OUTPUT_FOLDER': 'output',
            'POSTS': (("posts/*.txt", "posts", "post.tmpl"),),
            'POSTS_SECTIONS': True,
            'POSTS_SECTION_COLORS': {},
            'POSTS_SECTIONS_ARE_INDEXES': True,
            'POSTS_SECTION_DESCRIPTIONS': "",
            'POSTS_SECTION_FROM_META': False,
            'POSTS_SECTION_NAME': "",
            'POSTS_SECTION_TITLE': "{name}",
            'POSTS_SECTION_TRANSLATIONS': [],
            'POSTS_SECTION_TRANSLATIONS_ADD_DEFAULTS': False,
            'PRESERVE_EXIF_DATA': False,
            # TODO: change in v8
            'PAGES': (("stories/*.txt", "stories", "story.tmpl"),),
            'PANDOC_OPTIONS': [],
            'PRETTY_URLS': False,
            'FUTURE_IS_NOW': False,
            'INDEX_READ_MORE_LINK': DEFAULT_INDEX_READ_MORE_LINK,
            'REDIRECTIONS': [],
            'ROBOTS_EXCLUSIONS': [],
            'GENERATE_ATOM': False,
            'FEED_TEASERS': True,
            'FEED_PLAIN': False,
            'FEED_PREVIEWIMAGE': True,
            'FEED_READ_MORE_LINK': DEFAULT_FEED_READ_MORE_LINK,
            'FEED_LINKS_APPEND_QUERY': False,
            'GENERATE_RSS': True,
            'RSS_LINK': None,
            'RSS_PATH': '',
            'SASS_COMPILER': 'sass',
            'SASS_OPTIONS': [],
            'SEARCH_FORM': '',
            'SHOW_BLOG_TITLE': True,
            'SHOW_INDEX_PAGE_NAVIGATION': False,
            'SHOW_SOURCELINK': True,
            'SHOW_UNTRANSLATED_POSTS': True,
            'SLUG_AUTHOR_PATH': True,
            'SLUG_TAG_PATH': True,
            'SOCIAL_BUTTONS_CODE': '',
            'SITE_URL': 'https://example.com/',
            'PAGE_INDEX': False,
            'SECTION_PATH': '',
            'STRIP_INDEXES': False,
            'SITEMAP_INCLUDE_FILELESS_DIRS': True,
            'TAG_PATH': 'categories',
            'TAG_PAGES_ARE_INDEXES': False,
            'TAG_PAGES_DESCRIPTIONS': {},
            'TAG_PAGES_TITLES': {},
            'TAG_TRANSLATIONS': [],
            'TAG_TRANSLATIONS_ADD_DEFAULTS': False,
            'TAGS_INDEX_PATH': '',
            'TAGLIST_MINIMUM_POSTS': 1,
            'TEMPLATE_FILTERS': {},
            'THEME': 'bootstrap3',
            'THEME_COLOR': '#5670d4',  # light "corporate blue"
            'THUMBNAIL_SIZE': 180,
            'UNSLUGIFY_TITLES': False,  # WARNING: conf.py.in overrides this with True for backwards compatibility
            'URL_TYPE': 'rel_path',
            'USE_BASE_TAG': False,
            'USE_BUNDLES': True,
            'USE_CDN': False,
            'USE_CDN_WARNING': True,
            'USE_REST_DOCINFO_METADATA': False,
            'USE_FILENAME_AS_TITLE': True,
            'USE_KATEX': False,
            'USE_OPEN_GRAPH': True,
            'USE_SLUGIFY': True,
            'TIMEZONE': 'UTC',
            'WRITE_TAG_CLOUD': True,
            'DEPLOY_DRAFTS': True,
            'DEPLOY_FUTURE': False,
            'SCHEDULE_ALL': False,
            'SCHEDULE_RULE': '',
            'LOGGING_HANDLERS': {'stderr': {'loglevel': 'WARNING', 'bubble': True}},
            'DEMOTE_HEADERS': 1,
            'GITHUB_SOURCE_BRANCH': 'master',
            'GITHUB_DEPLOY_BRANCH': 'gh-pages',
            'GITHUB_REMOTE_NAME': 'origin',
            'GITHUB_COMMIT_SOURCE': False,  # WARNING: conf.py.in overrides this with True for backwards compatibility
            'META_GENERATOR_TAG': True,
        }

        # set global_context for template rendering
        self._GLOBAL_CONTEXT = {}

        self.config.update(config)

        # __builtins__ contains useless cruft
        if '__builtins__' in self.config:
            try:
                del self.config['__builtins__']
            except KeyError:
                del self.config[b'__builtins__']

        self.config['__colorful__'] = self.colorful
        self.config['__invariant__'] = self.invariant
        self.config['__quiet__'] = self.quiet

        # Make sure we have sane NAVIGATION_LINKS.
        if not self.config['NAVIGATION_LINKS']:
            self.config['NAVIGATION_LINKS'] = {self.config['DEFAULT_LANG']: ()}

        # Translatability configuration.
        self.config['TRANSLATIONS'] = self.config.get('TRANSLATIONS',
                                                      {self.config['DEFAULT_LANG']: ''})
        utils.TranslatableSetting.default_lang = self.config['DEFAULT_LANG']

        self.TRANSLATABLE_SETTINGS = ('BLOG_AUTHOR',
                                      'BLOG_TITLE',
                                      'BLOG_DESCRIPTION',
                                      'LICENSE',
                                      'CONTENT_FOOTER',
                                      'SOCIAL_BUTTONS_CODE',
                                      'SEARCH_FORM',
                                      'BODY_END',
                                      'EXTRA_HEAD_DATA',
                                      'NAVIGATION_LINKS',
                                      'FRONT_INDEX_HEADER',
                                      'INDEX_READ_MORE_LINK',
                                      'FEED_READ_MORE_LINK',
                                      'INDEXES_TITLE',
                                      'POSTS_SECTION_COLORS',
                                      'POSTS_SECTION_DESCRIPTIONS',
                                      'POSTS_SECTION_NAME',
                                      'POSTS_SECTION_TITLE',
                                      'INDEXES_PAGES',
                                      'INDEXES_PRETTY_PAGE_URL',
                                      # PATH options (Issue #1914)
                                      'TAG_PATH',
                                      'TAGS_INDEX_PATH',
                                      'CATEGORY_PATH',
                                      'CATEGORIES_INDEX_PATH',
                                      'SECTION_PATH',
                                      'INDEX_PATH',
                                      'RSS_PATH',
                                      'AUTHOR_PATH',
                                      'DATE_FORMAT',
                                      'JS_DATE_FORMAT',
                                      'RSS_COPYRIGHT',
                                      'RSS_COPYRIGHT_PLAIN',
                                      )

        self._GLOBAL_CONTEXT_TRANSLATABLE = ('blog_author',
                                             'blog_title',
                                             'blog_desc',  # TODO: remove in v8
                                             'blog_description',
                                             'license',
                                             'content_footer',
                                             'social_buttons_code',
                                             'search_form',
                                             'body_end',
                                             'extra_head_data',
                                             'date_format',
                                             'js_date_format',
                                             'posts_section_colors',
                                             'posts_section_descriptions',
                                             'posts_section_name',
                                             'posts_section_title',
                                             'front_index_header',
                                             )
        # WARNING: navigation_links SHOULD NOT be added to the list above.
        #          Themes ask for [lang] there and we should provide it.

        # We first have to massage JS_DATE_FORMAT, otherwise we run into trouble
        if 'JS_DATE_FORMAT' in self.config:
            if isinstance(self.config['JS_DATE_FORMAT'], dict):
                for k in self.config['JS_DATE_FORMAT']:
                    self.config['JS_DATE_FORMAT'][k] = json.dumps(self.config['JS_DATE_FORMAT'][k])
            else:
                self.config['JS_DATE_FORMAT'] = json.dumps(self.config['JS_DATE_FORMAT'])

        for i in self.TRANSLATABLE_SETTINGS:
            try:
                self.config[i] = utils.TranslatableSetting(i, self.config[i], self.config['TRANSLATIONS'])
            except KeyError:
                pass

        # A EXIF_WHITELIST implies you want to keep EXIF data
        if self.config['EXIF_WHITELIST'] and not self.config['PRESERVE_EXIF_DATA']:
            utils.LOGGER.warn('Setting EXIF_WHITELIST implies PRESERVE_EXIF_DATA is set to True')
            self.config['PRESERVE_EXIF_DATA'] = True

        # Setting PRESERVE_EXIF_DATA with an empty EXIF_WHITELIST implies 'keep everything'
        if self.config['PRESERVE_EXIF_DATA'] and not self.config['EXIF_WHITELIST']:
            utils.LOGGER.warn('You are setting PRESERVE_EXIF_DATA and not EXIF_WHITELIST so EXIF data is not really kept.')

        # Handle CONTENT_FOOTER and RSS_COPYRIGHT* properly.
        # We provide the arguments to format in CONTENT_FOOTER_FORMATS and RSS_COPYRIGHT_FORMATS.
        self.config['CONTENT_FOOTER'].langformat(self.config['CONTENT_FOOTER_FORMATS'])
        self.config['RSS_COPYRIGHT'].langformat(self.config['RSS_COPYRIGHT_FORMATS'])
        self.config['RSS_COPYRIGHT_PLAIN'].langformat(self.config['RSS_COPYRIGHT_FORMATS'])

        # propagate USE_SLUGIFY
        utils.USE_SLUGIFY = self.config['USE_SLUGIFY']

        # Make sure we have pyphen installed if we are using it
        if self.config.get('HYPHENATE') and pyphen is None:
            utils.LOGGER.warn('To use the hyphenation, you have to install '
                              'the "pyphen" package.')
            utils.LOGGER.warn('Setting HYPHENATE to False.')
            self.config['HYPHENATE'] = False

        # FIXME: Internally, we still use post_pages because it's a pain to change it
        self.config['post_pages'] = []
        for i1, i2, i3 in self.config['POSTS']:
            self.config['post_pages'].append([i1, i2, i3, True])
        for i1, i2, i3 in self.config['PAGES']:
            self.config['post_pages'].append([i1, i2, i3, False])

        # RSS_TEASERS has been replaced with FEED_TEASERS
        # TODO: remove on v8
        if 'RSS_TEASERS' in config:
            utils.LOGGER.warn('The RSS_TEASERS option is deprecated, use FEED_TEASERS instead.')
            if 'FEED_TEASERS' in config:
                utils.LOGGER.warn('FEED_TEASERS conflicts with RSS_TEASERS, ignoring RSS_TEASERS.')
            self.config['FEED_TEASERS'] = config['RSS_TEASERS']

        # RSS_PLAIN has been replaced with FEED_PLAIN
        # TODO: remove on v8
        if 'RSS_PLAIN' in config:
            utils.LOGGER.warn('The RSS_PLAIN option is deprecated, use FEED_PLAIN instead.')
            if 'FEED_PLAIN' in config:
                utils.LOGGER.warn('FEED_PLIN conflicts with RSS_PLAIN, ignoring RSS_PLAIN.')
            self.config['FEED_PLAIN'] = config['RSS_PLAIN']

        # RSS_LINKS_APPEND_QUERY has been replaced with FEED_LINKS_APPEND_QUERY
        # TODO: remove on v8
        if 'RSS_LINKS_APPEND_QUERY' in config:
            utils.LOGGER.warn('The RSS_LINKS_APPEND_QUERY option is deprecated, use FEED_LINKS_APPEND_QUERY instead.')
            if 'FEED_LINKS_APPEND_QUERY' in config:
                utils.LOGGER.warn('FEED_LINKS_APPEND_QUERY conflicts with RSS_LINKS_APPEND_QUERY, ignoring RSS_LINKS_APPEND_QUERY.')
            self.config['FEED_LINKS_APPEND_QUERY'] = config['RSS_LINKS_APPEND_QUERY']

        # RSS_READ_MORE_LINK has been replaced with FEED_READ_MORE_LINK
        # TODO: remove on v8
        if 'RSS_READ_MORE_LINK' in config:
            utils.LOGGER.warn('The RSS_READ_MORE_LINK option is deprecated, use FEED_READ_MORE_LINK instead.')
            if 'FEED_READ_MORE_LINK' in config:
                utils.LOGGER.warn('FEED_READ_MORE_LINK conflicts with RSS_READ_MORE_LINK, ignoring RSS_READ_MORE_LINK')
            self.config['FEED_READ_MORE_LINK'] = utils.TranslatableSetting('FEED_READ_MORE_LINK', config['RSS_READ_MORE_LINK'], self.config['TRANSLATIONS'])

        # DEFAULT_TRANSLATIONS_PATTERN was changed from "p.e.l" to "p.l.e"
        # TODO: remove on v8
        if 'TRANSLATIONS_PATTERN' not in self.config:
            if len(self.config.get('TRANSLATIONS', {})) > 1:
                utils.LOGGER.warn('You do not have a TRANSLATIONS_PATTERN set in your config, yet you have multiple languages.')
                utils.LOGGER.warn('Setting TRANSLATIONS_PATTERN to the pre-v6 default ("{path}.{ext}.{lang}").')
                utils.LOGGER.warn('Please add the proper pattern to your conf.py.  (The new default in v7 is "{0}".)'.format(DEFAULT_TRANSLATIONS_PATTERN))
                self.config['TRANSLATIONS_PATTERN'] = "{path}.{ext}.{lang}"
            else:
                # use v7 default there
                self.config['TRANSLATIONS_PATTERN'] = DEFAULT_TRANSLATIONS_PATTERN

        # HIDE_SOURCELINK has been replaced with the inverted SHOW_SOURCELINK
        # TODO: remove on v8
        if 'HIDE_SOURCELINK' in config:
            utils.LOGGER.warn('The HIDE_SOURCELINK option is deprecated, use SHOW_SOURCELINK instead.')
            if 'SHOW_SOURCELINK' in config:
                utils.LOGGER.warn('HIDE_SOURCELINK conflicts with SHOW_SOURCELINK, ignoring HIDE_SOURCELINK.')
            self.config['SHOW_SOURCELINK'] = not config['HIDE_SOURCELINK']

        # HIDE_UNTRANSLATED_POSTS has been replaced with the inverted SHOW_UNTRANSLATED_POSTS
        # TODO: remove on v8
        if 'HIDE_UNTRANSLATED_POSTS' in config:
            utils.LOGGER.warn('The HIDE_UNTRANSLATED_POSTS option is deprecated, use SHOW_UNTRANSLATED_POSTS instead.')
            if 'SHOW_UNTRANSLATED_POSTS' in config:
                utils.LOGGER.warn('HIDE_UNTRANSLATED_POSTS conflicts with SHOW_UNTRANSLATED_POSTS, ignoring HIDE_UNTRANSLATED_POSTS.')
            self.config['SHOW_UNTRANSLATED_POSTS'] = not config['HIDE_UNTRANSLATED_POSTS']

        # READ_MORE_LINK has been split into INDEX_READ_MORE_LINK and RSS_READ_MORE_LINK
        # TODO: remove on v8
        if 'READ_MORE_LINK' in config:
            utils.LOGGER.warn('The READ_MORE_LINK option is deprecated, use INDEX_READ_MORE_LINK and RSS_READ_MORE_LINK instead.')
            if 'INDEX_READ_MORE_LINK' in config:
                utils.LOGGER.warn('READ_MORE_LINK conflicts with INDEX_READ_MORE_LINK, ignoring READ_MORE_LINK.')
            else:
                self.config['INDEX_READ_MORE_LINK'] = utils.TranslatableSetting('INDEX_READ_MORE_LINK', config['READ_MORE_LINK'], self.config['TRANSLATIONS'])

            if 'RSS_READ_MORE_LINK' in config:
                utils.LOGGER.warn('READ_MORE_LINK conflicts with RSS_READ_MORE_LINK, ignoring READ_MORE_LINK.')
            else:
                self.config['RSS_READ_MORE_LINK'] = utils.TranslatableSetting('RSS_READ_MORE_LINK', config['READ_MORE_LINK'], self.config['TRANSLATIONS'])

        # Moot.it renamed themselves to muut.io
        # TODO: remove on v8?
        if self.config.get('COMMENT_SYSTEM') == 'moot':
            utils.LOGGER.warn('The moot comment system has been renamed to muut by the upstream.  Setting COMMENT_SYSTEM to "muut".')
            self.config['COMMENT_SYSTEM'] = 'muut'

        # Detect manually added KaTeX CSS (#2715/#2717)
        # TODO: remove on v8
        if any('katex.min.css' in v for v in self.config['EXTRA_HEAD_DATA'].values.values()):
            utils.LOGGER.warn("KaTeX CSS is now added by Nikola whenever needed (if your theme supports it). Please remove katex.min.css from EXTRA_HEAD_DATA in conf.py.")

        # Handle old plugin names (from before merging the taxonomy PR #2535)
        for old_plugin_name, new_plugin_names in TAXONOMY_COMPATIBILITY_PLUGIN_NAME_MAP.items():
            if old_plugin_name in self.config['DISABLED_PLUGINS']:
                missing_plugins = []
                for plugin_name in new_plugin_names:
                    if plugin_name not in self.config['DISABLED_PLUGINS']:
                        missing_plugins.append(plugin_name)
                if missing_plugins:
                    utils.LOGGER.warn('The "{}" plugin was replaced by several taxonomy plugins (see PR #2535): {}'.format(old_plugin_name, ', '.join(new_plugin_names)))
                    utils.LOGGER.warn('You are currently disabling "{}", but not the following new taxonomy plugins: {}'.format(old_plugin_name, ', '.join(missing_plugins)))
                    utils.LOGGER.warn('Please also disable these new plugins or remove "{}" from the DISABLED_PLUGINS list.'.format(old_plugin_name))
                    self.config['DISABLED_PLUGINS'].extend(missing_plugins)
        # Special-case logic for "render_indexes" to fix #2591
        if 'render_indexes' in self.config['DISABLED_PLUGINS']:
            if 'generate_rss' in self.config['DISABLED_PLUGINS'] or self.config['GENERATE_RSS'] is False:
                if 'classify_indexes' not in self.config['DISABLED_PLUGINS']:
                    utils.LOGGER.warn('You are disabling the "render_indexes" plugin, as well as disabling the "generate_rss" plugin or setting GENERATE_RSS to False. To achieve the same effect, please disable the "classify_indexes" plugin in the future.')
                    self.config['DISABLED_PLUGINS'].append('classify_indexes')
            else:
                if not self.config['DISABLE_INDEXES_PLUGIN_INDEX_AND_ATOM_FEED']:
                    utils.LOGGER.warn('You are disabling the "render_indexes" plugin, but not the generation of RSS feeds. Please put "DISABLE_INDEXES_PLUGIN_INDEX_AND_ATOM_FEED = True" into your configuration instead.')
                    self.config['DISABLE_INDEXES_PLUGIN_INDEX_AND_ATOM_FEED'] = True

        # Disable RSS.  For a successful disable, we must have both the option
        # false and the plugin disabled through the official means.
        if 'generate_rss' in self.config['DISABLED_PLUGINS'] and self.config['GENERATE_RSS'] is True:
            utils.LOGGER.warn('Please use GENERATE_RSS to disable RSS feed generation, instead of mentioning generate_rss in DISABLED_PLUGINS.')
            self.config['GENERATE_RSS'] = False
            self.config['DISABLE_INDEXES_PLUGIN_RSS_FEED'] = True

        # PRETTY_URLS defaults to enabling STRIP_INDEXES unless explicitly disabled
        if self.config.get('PRETTY_URLS') and 'STRIP_INDEXES' not in config:
            self.config['STRIP_INDEXES'] = True

        if 'LISTINGS_FOLDER' in config:
            if 'LISTINGS_FOLDERS' not in config:
                utils.LOGGER.warn("The LISTINGS_FOLDER option is deprecated, use LISTINGS_FOLDERS instead.")
                self.config['LISTINGS_FOLDERS'] = {self.config['LISTINGS_FOLDER']: self.config['LISTINGS_FOLDER']}
                utils.LOGGER.warn("LISTINGS_FOLDERS = {0}".format(self.config['LISTINGS_FOLDERS']))
            else:
                utils.LOGGER.warn("Both LISTINGS_FOLDER and LISTINGS_FOLDERS are specified, ignoring LISTINGS_FOLDER.")

        if 'GALLERY_PATH' in config:
            if 'GALLERY_FOLDERS' not in config:
                utils.LOGGER.warn("The GALLERY_PATH option is deprecated, use GALLERY_FOLDERS instead.")
                self.config['GALLERY_FOLDERS'] = {self.config['GALLERY_PATH']: self.config['GALLERY_PATH']}
                utils.LOGGER.warn("GALLERY_FOLDERS = {0}".format(self.config['GALLERY_FOLDERS']))
            else:
                utils.LOGGER.warn("Both GALLERY_PATH and GALLERY_FOLDERS are specified, ignoring GALLERY_PATH.")

        if not self.config.get('COPY_SOURCES'):
            self.config['SHOW_SOURCELINK'] = False

        if self.config['CATEGORY_PATH']._inp is None:
            self.config['CATEGORY_PATH'] = self.config['TAG_PATH']
        if self.config['CATEGORY_PAGES_ARE_INDEXES'] is None:
            self.config['CATEGORY_PAGES_ARE_INDEXES'] = self.config['TAG_PAGES_ARE_INDEXES']

        self.default_lang = self.config['DEFAULT_LANG']
        self.translations = self.config['TRANSLATIONS']

        locale_fallback, locale_default, locales = sanitized_locales(
            self.config.get('LOCALE_FALLBACK', None),
            self.config.get('LOCALE_DEFAULT', None),
            self.config.get('LOCALES', {}), self.translations)
        utils.LocaleBorg.initialize(locales, self.default_lang)

        # BASE_URL defaults to SITE_URL
        if 'BASE_URL' not in self.config:
            self.config['BASE_URL'] = self.config.get('SITE_URL')
        # BASE_URL should *always* end in /
        if self.config['BASE_URL'] and self.config['BASE_URL'][-1] != '/':
            utils.LOGGER.warn("Your BASE_URL doesn't end in / -- adding it, but please fix it in your config file!")
            self.config['BASE_URL'] += '/'

        try:
            _bnl = urlsplit(self.config['BASE_URL']).netloc
            _bnl.encode('ascii')
            urlsplit(self.config['SITE_URL']).netloc.encode('ascii')
        except (UnicodeEncodeError, UnicodeDecodeError):
            utils.LOGGER.error("Your BASE_URL or SITE_URL contains an IDN expressed in Unicode.  Please convert it to Punycode.")
            utils.LOGGER.error("Punycode of {}: {}".format(_bnl, _bnl.encode('idna')))
            sys.exit(1)

        # TODO: remove in v8
        if not isinstance(self.config['DEPLOY_COMMANDS'], dict):
            utils.LOGGER.warn("A single list as DEPLOY_COMMANDS is deprecated.  DEPLOY_COMMANDS should be a dict, with deploy preset names as keys and lists of commands as values.")
            utils.LOGGER.warn("The key `default` is used by `nikola deploy`:")
            self.config['DEPLOY_COMMANDS'] = {'default': self.config['DEPLOY_COMMANDS']}
            utils.LOGGER.warn("DEPLOY_COMMANDS = {0}".format(self.config['DEPLOY_COMMANDS']))
            utils.LOGGER.info("(The above can be used with `nikola deploy` or `nikola deploy default`.  Multiple presets are accepted.)")

        # TODO: remove and change default in v8
        if 'BLOG_TITLE' in config and 'WRITE_TAG_CLOUD' not in config:
            # BLOG_TITLE is a hack, otherwise the warning would be displayed
            # when conf.py does not exist
            utils.LOGGER.warn("WRITE_TAG_CLOUD is not set in your config.  Defaulting to True (== writing tag_cloud_data.json).")
            utils.LOGGER.warn("Please explicitly add the setting to your conf.py with the desired value, as the setting will default to False in the future.")

        # Rename stories to pages (#1891, #2518)
        # TODO: remove in v8
        if 'COMMENTS_IN_STORIES' in config:
            utils.LOGGER.warn('The COMMENTS_IN_STORIES option is deprecated, use COMMENTS_IN_PAGES instead.')
            self.config['COMMENTS_IN_PAGES'] = config['COMMENTS_IN_STORIES']
        if 'STORY_INDEX' in config:
            utils.LOGGER.warn('The STORY_INDEX option is deprecated, use PAGE_INDEX instead.')
            self.config['PAGE_INDEX'] = config['STORY_INDEX']

        if 'POSTS_SECTION_ARE_INDEXES' in config:
            utils.LOGGER.warn('The POSTS_SECTION_ARE_INDEXES option is deprecated, use POSTS_SECTIONS_ARE_INDEXES instead.')
            self.config['POSTS_SECTIONS_ARE_INDEXES'] = config['POSTS_SECTION_ARE_INDEXES']

        # TODO: remove in v8, or earlier
        if ('THEME_REVEAL_CONFIG_SUBTHEME' in config or 'THEME_REVEAL_CONFIG_TRANSITION' in config or
                (self.config['THEME'] in ('reveal', 'reveal-jinja') and
                 ('subtheme' not in config['GLOBAL_CONTEXT'] or 'transition' not in config['GLOBAL_CONTEXT']))):
            utils.LOGGER.warn('The THEME_REVEAL_CONFIG_* settings are deprecated. Use `subtheme` and `transition` in GLOBAL_CONTEXT instead.')
            self._GLOBAL_CONTEXT['subtheme'] = config.get('THEME_REVEAL_CONFIG_SUBTHEME', 'sky')
            self._GLOBAL_CONTEXT['transition'] = config.get('THEME_REVEAL_CONFIG_TRANSITION', 'cube')

        # The pelican metadata format requires a markdown extension
        if config.get('METADATA_FORMAT', 'nikola').lower() == 'pelican':
            if 'markdown.extensions.meta' not in config.get('MARKDOWN_EXTENSIONS', []) \
                    and 'markdown' in self.config['COMPILERS']:
                utils.LOGGER.warn(
                    'To use the pelican metadata format you need to add '
                    '"markdown.extensions.meta" to your MARKDOWN_EXTENSIONS setting.')

        # We use one global tzinfo object all over Nikola.
        try:
            self.tzinfo = dateutil.tz.gettz(self.config['TIMEZONE'])
        except Exception as exc:
            utils.LOGGER.warn("Error getting TZ: {}", exc)
            self.tzinfo = dateutil.tz.gettz()
        self.config['__tzinfo__'] = self.tzinfo

        # Store raw compilers for internal use (need a copy for that)
        self.config['_COMPILERS_RAW'] = {}
        for k, v in self.config['COMPILERS'].items():
            self.config['_COMPILERS_RAW'][k] = list(v)

        # Get search path for themes
        self.themes_dirs = ['themes'] + self.config['EXTRA_THEMES_DIRS']

        # Register default filters
        filter_name_format = 'filters.{0}'
        for filter_name, filter_definition in filters.__dict__.items():
            # Ignore objects whose name starts with an underscore, or which are not callable
            if filter_name.startswith('_') or not callable(filter_definition):
                continue
            # Register all other objects as filters
            self.register_filter(filter_name_format.format(filter_name), filter_definition)

        self._set_global_context_from_config()
        # Read data files only if a site exists (Issue #2708)
        if self.configured:
            self._set_global_context_from_data()

        # Set persistent state facility
        self.state = Persistor('state_data.json')

        # Set cache facility
        self.cache = Persistor(os.path.join(self.config['CACHE_FOLDER'], 'cache_data.json'))

        # Create directories for persistors only if a site exists (Issue #2334)
        if self.configured:
            self.state._set_site(self)
            self.cache._set_site(self)