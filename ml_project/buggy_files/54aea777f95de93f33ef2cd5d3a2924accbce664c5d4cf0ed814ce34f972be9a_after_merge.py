        def __call__(self, tag, default):
            return 0 if '~#' in tag[:2] else self.comma(tag)