    def __init__(self, main_config, main_section, target):
        self.config = ServiceConfig(self.CONFIG_PREFIX, main_config, target)
        self.main_section = main_section
        self.main_config = main_config
        self.target = target

        self.desc_len = self._get_config_or_default('description_length', 35, asint);
        self.anno_len = self._get_config_or_default('annotation_length', 45, asint);
        self.inline_links = self._get_config_or_default('inline_links', True, asbool);
        self.annotation_links = self._get_config_or_default('annotation_links', not self.inline_links, asbool)
        self.annotation_comments = self._get_config_or_default('annotation_comments', True, asbool)
        self.shorten = self._get_config_or_default('shorten', False, asbool)
        self.default_priority = self._get_config_or_default('default_priority','M')

        self.add_tags = []
        if 'add_tags' in self.config:
            for raw_option in self.config.get('add_tags').split(','):
                option = raw_option.strip(' +;')
                if option:
                    self.add_tags.append(option)

        log.info("Working on [%s]", self.target)