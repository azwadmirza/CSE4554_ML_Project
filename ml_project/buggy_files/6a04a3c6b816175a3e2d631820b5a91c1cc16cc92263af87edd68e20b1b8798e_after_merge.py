    def loadSettings(self):
        data = session.query(Settings).first()  # type: Settings

        self.config_calibre_dir = data.config_calibre_dir
        self.config_port = data.config_port
        self.config_certfile = data.config_certfile
        self.config_keyfile  = data.config_keyfile
        self.config_calibre_web_title = data.config_calibre_web_title
        self.config_books_per_page = data.config_books_per_page
        self.config_random_books = data.config_random_books
        self.config_authors_max = data.config_authors_max
        self.config_title_regex = data.config_title_regex
        self.config_read_column = data.config_read_column
        self.config_log_level = data.config_log_level
        self.config_uploading = data.config_uploading
        self.config_anonbrowse = data.config_anonbrowse
        self.config_public_reg = data.config_public_reg
        self.config_default_role = data.config_default_role
        self.config_default_show = data.config_default_show
        self.config_columns_to_ignore = data.config_columns_to_ignore
        self.config_use_google_drive = data.config_use_google_drive
        self.config_google_drive_folder = data.config_google_drive_folder
        self.config_ebookconverter = data.config_ebookconverter
        self.config_converterpath = data.config_converterpath
        self.config_calibre = data.config_calibre
        if data.config_google_drive_watch_changes_response:
            self.config_google_drive_watch_changes_response = json.loads(data.config_google_drive_watch_changes_response)
        else:
            self.config_google_drive_watch_changes_response=None
        self.config_columns_to_ignore = data.config_columns_to_ignore
        self.db_configured = bool(self.config_calibre_dir is not None and
                (not self.config_use_google_drive or os.path.exists(self.config_calibre_dir + '/metadata.db')))
        self.config_remote_login = data.config_remote_login
        self.config_use_goodreads = data.config_use_goodreads
        self.config_goodreads_api_key = data.config_goodreads_api_key
        self.config_goodreads_api_secret = data.config_goodreads_api_secret
        if data.config_mature_content_tags:
            self.config_mature_content_tags = data.config_mature_content_tags
        else:
            self.config_mature_content_tags = u''
        if data.config_logfile:
            self.config_logfile = data.config_logfile
        self.config_rarfile_location = data.config_rarfile_location
        self.config_theme = data.config_theme
        self.config_updatechannel = data.config_updatechannel