    def check_language(self, languages):
        # Cut additional Subtitles
        languages = languages.split('|', 1)[0]

        language_list = re.split(r'[,&]', languages)

        try:
            if self.config['language'] == 'german':
                if regex_is_german.search(language_list[0]):
                    return True
            elif self.config['language'] == 'foreign':
                if (regex_is_foreign.search(language_list[0]) and len(language_list) == 1) or \
                        (len(language_list) > 1 and not regex_is_subtitle.search(language_list[1])):
                    return True
            elif self.config['language'] == 'subtitle':
                if len(language_list) > 1 and regex_is_subtitle.search(language_list[1]):
                    return True
            elif self.config['language'] == 'dual':
                if len(language_list) > 1 and not regex_is_subtitle.search(language_list[1]):
                    return True
        except (KeyError, re.error):
            pass

        return False