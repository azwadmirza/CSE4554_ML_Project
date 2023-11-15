    def set_site(self, site):
        site.register_path_handler('gallery', self.gallery_path)
        site.register_path_handler('gallery_global', self.gallery_global_path)
        site.register_path_handler('gallery_rss', self.gallery_rss_path)

        self.logger = utils.get_logger('render_galleries', site.loghandlers)

        self.kw = {
            'thumbnail_size': site.config['THUMBNAIL_SIZE'],
            'max_image_size': site.config['MAX_IMAGE_SIZE'],
            'output_folder': site.config['OUTPUT_FOLDER'],
            'cache_folder': site.config['CACHE_FOLDER'],
            'default_lang': site.config['DEFAULT_LANG'],
            'use_filename_as_title': site.config['USE_FILENAME_AS_TITLE'],
            'gallery_folders': site.config['GALLERY_FOLDERS'],
            'sort_by_date': site.config['GALLERY_SORT_BY_DATE'],
            'filters': site.config['FILTERS'],
            'translations': site.config['TRANSLATIONS'],
            'global_context': site.GLOBAL_CONTEXT,
            'feed_length': site.config['FEED_LENGTH'],
            'tzinfo': site.tzinfo,
            'comments_in_galleries': site.config['COMMENTS_IN_GALLERIES'],
            'generate_rss': site.config['GENERATE_RSS'],
        }

        # Verify that no folder in GALLERY_FOLDERS appears twice
        appearing_paths = set()
        for source, dest in self.kw['gallery_folders'].items():
            if source in appearing_paths or dest in appearing_paths:
                problem = source if source in appearing_paths else dest
                utils.LOGGER.error("The gallery input or output folder '{0}' appears in more than one entry in GALLERY_FOLDERS, exiting.".format(problem))
                sys.exit(1)
            appearing_paths.add(source)
            appearing_paths.add(dest)

        # Find all galleries we need to process
        self.find_galleries()
        # Create self.gallery_links
        self.create_galleries_paths()

        return super(Galleries, self).set_site(site)