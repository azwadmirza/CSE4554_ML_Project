    def get_localizations(self, basepath):
        """Returns all localization items for this object and all descendant objects"""
        for path in self.get_subpaths(basepath):
            for child in self.children:
                if isinstance(child, LocaleCleanerPath):
                    for res in child.get_localizations(path):
                        yield res
                elif isinstance(child, Pattern):
                    for element in os.listdir(path):
                        match = child.match(element)
                        if match is not None:
                            yield (match.group('locale'),
                                   match.group('specifier'),
                                   os.path.join(path, element))