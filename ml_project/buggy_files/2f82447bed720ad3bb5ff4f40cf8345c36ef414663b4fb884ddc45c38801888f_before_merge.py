    def init(self):
        if url_normalize is None:
            raise ValueError("Could not import 'url-normalize'. Please install it.")
        if get_tld is None:
            raise ValueError("Could not import 'tld'. Please install it.")
        update_tld_names()
        self.domain_whitelist = []
        if getattr(self.parameters, "domain_whitelist", '') != '':
            self.domain_whitelist.extend(self.parameters.domain_whitelist.split(','))
        self.substitutions = []
        if getattr(self.parameters, "substitutions", '') != '':
            temp = self.parameters.substitutions.split(';')
            if len(temp) % 2 != 0:
                raise InvalidArgument(
                    'substitutions',
                    got=self.parameters.substitutions,
                    expected="even number of ; separeted strings")
            for i in range(int(len(temp) / 2)):
                self.substitutions.append([temp[2 * i], temp[2 * i + 1]])
        self.classification_type = getattr(self.parameters, "classification_type", "unknown")
        if not ClassificationType.is_valid(self.classification_type):
            self.classification_type = 'unknown'