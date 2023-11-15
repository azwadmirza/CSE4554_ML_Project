    def __init__(self, **config):
        """Setup proper environment for running tasks."""

        # Register our own path handlers
        self.path_handlers = {
            'slug': self.slug_path,
            'post_path': self.post_path,
            'filename': self.filename_path,
        }

        self.strict = False
        self.global_data = {}
        self.posts = []
        self.posts_per_year = defaultdict(list)
        self.posts_per_month = defaultdict(list)
        self.posts_per_tag = defaultdict(list)
        self.posts_per_category = defaultdict(list)
        self.post_per_file = {}
        self.timeline = []
        self.pages = []
        self._scanned = False
        self._template_system = None
        self._THEMES = None
        self.debug = DEBUG
        self.loghandlers = []
        self.colorful = config.pop('__colorful__', False)
        self.invariant = config.pop('__invariant__', False)
        self.quiet = config.pop('__quiet__', False)
        self.configured = bool(config)

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
            'BLOG_AUTHOR': 'Default Author',
            'BLOG_TITLE': 'Default Title',
            'BLOG_DESCRIPTION': 'Default Description',
            'BODY_END': "",
            'CACHE_FOLDER': 'cache',
            'CODE_COLOR_SCHEME': 'default',
            'COMMENT_SYSTEM': 'disqus',
            'COMMENTS_IN_GALLERIES': False,
            'COMMENTS_IN_STORIES': False,
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
            'COPY_SOURCES': True,
            'CREATE_MONTHLY_ARCHIVE': False,
            'CREATE_SINGLE_ARCHIVE': False,
            'DATE_FORMAT': '%Y-%m-%d %H:%M',
            'DEFAULT_LANG': "en",
            'DEPLOY_COMMANDS': [],
            'DISABLED_PLUGINS': [],
            'EXTRA_PLUGINS_DIRS': [],
            'COMMENT_SYSTEM_ID': 'nikolademo',
            'EXTRA_HEAD_DATA': '',
            'FAVICONS': {},
            'FEED_LENGTH': 10,
            'FILE_METADATA_REGEXP': None,
            'ADDITIONAL_METADATA': {},
            'FILES_FOLDERS': {'files': ''},
            'FILTERS': {},
            'FORCE_ISO8601': False,
            'GALLERY_PATH': 'galleries',
            'GALLERY_SORT_BY_DATE': True,
            'GZIP_COMMAND': None,
            'GZIP_FILES': False,
            'GZIP_EXTENSIONS': ('.txt', '.htm', '.html', '.css', '.js', '.json', '.xml'),
            'HYPHENATE': False,
            'INDEX_DISPLAY_POST_COUNT': 10,
            'INDEX_FILE': 'index.html',
            'INDEX_TEASERS': False,
            'INDEXES_TITLE': "",
            'INDEXES_PAGES': "",
            'INDEXES_PAGES_MAIN': False,
            'INDEX_PATH': '',
            'IPYNB_CONFIG': {},
            'LESS_COMPILER': 'lessc',
            'LESS_OPTIONS': [],
            'LICENSE': '',
            'LINK_CHECK_WHITELIST': [],
            'LISTINGS_FOLDER': 'listings',
            'LOGO_URL': '',
            'NAVIGATION_LINKS': {},
            'MARKDOWN_EXTENSIONS': ['fenced_code', 'codehilite'],
            'MAX_IMAGE_SIZE': 1280,
            'MATHJAX_CONFIG': '',
            'OLD_THEME_SUPPORT': True,
            'OUTPUT_FOLDER': 'output',
            'POSTS': (("posts/*.txt", "posts", "post.tmpl"),),
            'PAGES': (("stories/*.txt", "stories", "story.tmpl"),),
            'PRETTY_URLS': False,
            'FUTURE_IS_NOW': False,
            'INDEX_READ_MORE_LINK': DEFAULT_INDEX_READ_MORE_LINK,
            'RSS_READ_MORE_LINK': DEFAULT_RSS_READ_MORE_LINK,
            'REDIRECTIONS': [],
            'ROBOTS_EXCLUSIONS': [],
            'GENERATE_RSS': True,
            'RSS_LINK': None,
            'RSS_PATH': '',
            'RSS_PLAIN': False,
            'RSS_TEASERS': True,
            'SASS_COMPILER': 'sass',
            'SASS_OPTIONS': [],
            'SEARCH_FORM': '',
            'SHOW_BLOG_TITLE': True,
            'SHOW_SOURCELINK': True,
            'SHOW_UNTRANSLATED_POSTS': True,
            'SLUG_TAG_PATH': True,
            'SOCIAL_BUTTONS_CODE': SOCIAL_BUTTONS_CODE,
            'SITE_URL': 'http://getnikola.com/',
            'STORY_INDEX': False,
            'STRIP_INDEXES': False,
            'SITEMAP_INCLUDE_FILELESS_DIRS': True,
            'TAG_PATH': 'categories',
            'TAG_PAGES_ARE_INDEXES': False,
            'TEMPLATE_FILTERS': {},
            'THEME': 'bootstrap',
            'THEME_REVEAL_CONFIG_SUBTHEME': 'sky',
            'THEME_REVEAL_CONFIG_TRANSITION': 'cube',
            'THUMBNAIL_SIZE': 180,
            'UNSLUGIFY_TITLES': False,  # WARNING: conf.py.in overrides this with True for backwards compatibility
            'URL_TYPE': 'rel_path',
            'USE_BUNDLES': True,
            'USE_CDN': False,
            'USE_FILENAME_AS_TITLE': True,
            'USE_OPEN_GRAPH': True,
            'TIMEZONE': 'UTC',
            'DEPLOY_DRAFTS': True,
            'DEPLOY_FUTURE': False,
            'SCHEDULE_ALL': False,
            'SCHEDULE_RULE': '',
            'LOGGING_HANDLERS': {'stderr': {'loglevel': 'WARNING', 'bubble': True}},
            'DEMOTE_HEADERS': 1,
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
                                      'INDEX_READ_MORE_LINK',
                                      'RSS_READ_MORE_LINK',)

        self._GLOBAL_CONTEXT_TRANSLATABLE = ('blog_author',
                                             'blog_title',
                                             'blog_desc',  # TODO: remove in v8
                                             'blog_description',
                                             'license',
                                             'content_footer',
                                             'social_buttons_code',
                                             'search_form',
                                             'body_end',
                                             'extra_head_data',)
        # WARNING: navigation_links SHOULD NOT be added to the list above.
        #          Themes ask for [lang] there and we should provide it.

        for i in self.TRANSLATABLE_SETTINGS:
            try:
                self.config[i] = utils.TranslatableSetting(i, self.config[i], self.config['TRANSLATIONS'])
            except KeyError:
                pass

        # Handle CONTENT_FOOTER properly.
        # We provide the arguments to format in CONTENT_FOOTER_FORMATS.
        self.config['CONTENT_FOOTER'].langformat(self.config['CONTENT_FOOTER_FORMATS'])

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

        # Disable RSS.  For a successful disable, we must have both the option
        # false and the plugin disabled through the official means.
        if 'generate_rss' in self.config['DISABLED_PLUGINS']:
            self.config['GENERATE_RSS'] = False

        if not self.config['GENERATE_RSS'] and 'generate_rss' not in self.config['DISABLED_PLUGINS']:
            self.config['DISABLED_PLUGINS'].append('generate_rss')

        # PRETTY_URLS defaults to enabling STRIP_INDEXES unless explicitly disabled
        if self.config.get('PRETTY_URLS') and 'STRIP_INDEXES' not in config:
            self.config['STRIP_INDEXES'] = True

        if not self.config.get('COPY_SOURCES'):
            self.config['SHOW_SOURCELINK'] = False

        self.default_lang = self.config['DEFAULT_LANG']
        self.translations = self.config['TRANSLATIONS']

        if self.configured:
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
            utils.LOGGER.warn("Your BASE_URL doesn't end in / -- adding it.")

        # We use one global tzinfo object all over Nikola.
        self.tzinfo = dateutil.tz.gettz(self.config['TIMEZONE'])
        self.config['__tzinfo__'] = self.tzinfo

        self.plugin_manager = PluginManager(categories_filter={
            "Command": Command,
            "Task": Task,
            "LateTask": LateTask,
            "TemplateSystem": TemplateSystem,
            "PageCompiler": PageCompiler,
            "TaskMultiplier": TaskMultiplier,
            "RestExtension": RestExtension,
            "MarkdownExtension": MarkdownExtension,
            "SignalHandler": SignalHandler,
        })
        self.plugin_manager.setPluginInfoExtension('plugin')
        extra_plugins_dirs = self.config['EXTRA_PLUGINS_DIRS']
        if sys.version_info[0] == 3:
            places = [
                resource_filename('nikola', 'plugins'),
                os.path.join(os.getcwd(), 'plugins'),
                os.path.expanduser('~/.nikola/plugins'),
            ] + [path for path in extra_plugins_dirs if path]
        else:
            places = [
                resource_filename('nikola', utils.sys_encode('plugins')),
                os.path.join(os.getcwd(), utils.sys_encode('plugins')),
                os.path.expanduser('~/.nikola/plugins'),
            ] + [utils.sys_encode(path) for path in extra_plugins_dirs if path]

        self.plugin_manager.setPluginPlaces(places)
        self.plugin_manager.collectPlugins()

        # Activate all required SignalHandler plugins
        for plugin_info in self.plugin_manager.getPluginsOfCategory("SignalHandler"):
            if plugin_info.name in self.config.get('DISABLED_PLUGINS'):
                self.plugin_manager.removePluginFromCategory(plugin_info, "SignalHandler")
            else:
                self.plugin_manager.activatePluginByName(plugin_info.name)
                plugin_info.plugin_object.set_site(self)

        # Emit signal for SignalHandlers which need to start running immediately.
        signal('sighandlers_loaded').send(self)

        self._commands = {}
        # Activate all command plugins
        for plugin_info in self.plugin_manager.getPluginsOfCategory("Command"):
            if plugin_info.name in self.config['DISABLED_PLUGINS']:
                self.plugin_manager.removePluginFromCategory(plugin_info, "Command")
                continue

            self.plugin_manager.activatePluginByName(plugin_info.name)
            plugin_info.plugin_object.set_site(self)
            plugin_info.plugin_object.short_help = plugin_info.description
            self._commands[plugin_info.name] = plugin_info.plugin_object

        # Activate all task plugins
        for task_type in ["Task", "LateTask"]:
            for plugin_info in self.plugin_manager.getPluginsOfCategory(task_type):
                if plugin_info.name in self.config['DISABLED_PLUGINS']:
                    self.plugin_manager.removePluginFromCategory(plugin_info, task_type)
                    continue
                self.plugin_manager.activatePluginByName(plugin_info.name)
                plugin_info.plugin_object.set_site(self)

        # Activate all multiplier plugins
        for plugin_info in self.plugin_manager.getPluginsOfCategory("TaskMultiplier"):
            if plugin_info.name in self.config['DISABLED_PLUGINS']:
                self.plugin_manager.removePluginFromCategory(plugin_info, task_type)
                continue
            self.plugin_manager.activatePluginByName(plugin_info.name)
            plugin_info.plugin_object.set_site(self)

        compilers = defaultdict(set)
        # Also add aliases for combinations with TRANSLATIONS_PATTERN
        for compiler, exts in self.config['COMPILERS'].items():
            for ext in exts:
                compilers[compiler].add(ext)
                for lang in self.config['TRANSLATIONS'].keys():
                    candidate = utils.get_translation_candidate(self.config, "f" + ext, lang)
                    compilers[compiler].add(candidate)

        # Avoid redundant compilers
        for k, v in compilers.items():
            self.config['COMPILERS'][k] = sorted(list(v))

        # Activate all required compiler plugins
        for plugin_info in self.plugin_manager.getPluginsOfCategory("PageCompiler"):
            if plugin_info.name in self.config["COMPILERS"].keys():
                self.plugin_manager.activatePluginByName(plugin_info.name)
                plugin_info.plugin_object.set_site(self)

        self._GLOBAL_CONTEXT['url_type'] = self.config['URL_TYPE']
        self._GLOBAL_CONTEXT['timezone'] = self.tzinfo
        self._GLOBAL_CONTEXT['_link'] = self.link
        self._GLOBAL_CONTEXT['set_locale'] = utils.LocaleBorg().set_locale
        self._GLOBAL_CONTEXT['rel_link'] = self.rel_link
        self._GLOBAL_CONTEXT['abs_link'] = self.abs_link
        self._GLOBAL_CONTEXT['exists'] = self.file_exists
        self._GLOBAL_CONTEXT['SLUG_TAG_PATH'] = self.config['SLUG_TAG_PATH']
        self._GLOBAL_CONTEXT['annotations'] = self.config['ANNOTATIONS']
        self._GLOBAL_CONTEXT['index_display_post_count'] = self.config[
            'INDEX_DISPLAY_POST_COUNT']
        self._GLOBAL_CONTEXT['use_bundles'] = self.config['USE_BUNDLES']
        self._GLOBAL_CONTEXT['use_cdn'] = self.config.get("USE_CDN")
        self._GLOBAL_CONTEXT['favicons'] = self.config['FAVICONS']
        self._GLOBAL_CONTEXT['date_format'] = self.config.get(
            'DATE_FORMAT', '%Y-%m-%d %H:%M')
        self._GLOBAL_CONTEXT['blog_author'] = self.config.get('BLOG_AUTHOR')
        self._GLOBAL_CONTEXT['blog_title'] = self.config.get('BLOG_TITLE')
        self._GLOBAL_CONTEXT['show_blog_title'] = self.config.get('SHOW_BLOG_TITLE')
        self._GLOBAL_CONTEXT['logo_url'] = self.config.get('LOGO_URL')
        self._GLOBAL_CONTEXT['blog_description'] = self.config.get('BLOG_DESCRIPTION')

        # TODO: remove in v8
        self._GLOBAL_CONTEXT['blog_desc'] = self.config.get('BLOG_DESCRIPTION')

        self._GLOBAL_CONTEXT['blog_url'] = self.config.get('SITE_URL')
        self._GLOBAL_CONTEXT['template_hooks'] = self.template_hooks
        self._GLOBAL_CONTEXT['body_end'] = self.config.get('BODY_END')
        self._GLOBAL_CONTEXT['social_buttons_code'] = self.config.get('SOCIAL_BUTTONS_CODE')
        self._GLOBAL_CONTEXT['translations'] = self.config.get('TRANSLATIONS')
        self._GLOBAL_CONTEXT['license'] = self.config.get('LICENSE')
        self._GLOBAL_CONTEXT['search_form'] = self.config.get('SEARCH_FORM')
        self._GLOBAL_CONTEXT['comment_system'] = self.config.get('COMMENT_SYSTEM')
        self._GLOBAL_CONTEXT['comment_system_id'] = self.config.get('COMMENT_SYSTEM_ID')
        self._GLOBAL_CONTEXT['site_has_comments'] = bool(self.config.get('COMMENT_SYSTEM'))
        self._GLOBAL_CONTEXT['mathjax_config'] = self.config.get(
            'MATHJAX_CONFIG')
        self._GLOBAL_CONTEXT['subtheme'] = self.config.get('THEME_REVEAL_CONFIG_SUBTHEME')
        self._GLOBAL_CONTEXT['transition'] = self.config.get('THEME_REVEAL_CONFIG_TRANSITION')
        self._GLOBAL_CONTEXT['content_footer'] = self.config.get(
            'CONTENT_FOOTER')
        self._GLOBAL_CONTEXT['generate_rss'] = self.config.get('GENERATE_RSS')
        self._GLOBAL_CONTEXT['rss_path'] = self.config.get('RSS_PATH')
        self._GLOBAL_CONTEXT['rss_link'] = self.config.get('RSS_LINK')

        self._GLOBAL_CONTEXT['navigation_links'] = self.config.get('NAVIGATION_LINKS')

        self._GLOBAL_CONTEXT['use_open_graph'] = self.config.get(
            'USE_OPEN_GRAPH', True)
        self._GLOBAL_CONTEXT['twitter_card'] = self.config.get(
            'TWITTER_CARD', {})
        self._GLOBAL_CONTEXT['hide_sourcelink'] = not self.config.get(
            'SHOW_SOURCELINK')
        self._GLOBAL_CONTEXT['show_sourcelink'] = self.config.get(
            'SHOW_SOURCELINK')
        self._GLOBAL_CONTEXT['extra_head_data'] = self.config.get('EXTRA_HEAD_DATA')
        self._GLOBAL_CONTEXT['colorbox_locales'] = LEGAL_VALUES['COLORBOX_LOCALES']

        self._GLOBAL_CONTEXT.update(self.config.get('GLOBAL_CONTEXT', {}))

        # Load compiler plugins
        self.compilers = {}
        self.inverse_compilers = {}

        for plugin_info in self.plugin_manager.getPluginsOfCategory(
                "PageCompiler"):
            self.compilers[plugin_info.name] = \
                plugin_info.plugin_object

        signal('configured').send(self)