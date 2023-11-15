    def init_app(self, app):
        self.config.update(app.config)
        # get environment variables
        self.config.update({
            key: self.__coerce_value(os.environ.get(key, value))
            for key, value in DEFAULT_CONFIG.items()
        })
        self.resolve_host()

        # automatically set the sqlalchemy string
        if self.config['DB_FLAVOR']:
            template = self.DB_TEMPLATES[self.config['DB_FLAVOR']]
            self.config['SQLALCHEMY_DATABASE_URI'] = template.format(**self.config)
        # update the app config itself
        app.config = self