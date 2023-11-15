    def __iadd__(self, other):
        warnings.warn('builder.css_files is deprecated. '
                      'Please use app.add_stylesheet() instead.',
                      RemovedInSphinx20Warning)
        for item in other:
            self.append(item)
        return self