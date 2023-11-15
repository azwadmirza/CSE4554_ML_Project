    def __init__(self, template_path: Union[str, List[str]] = None, language: str = None) -> None:  # NOQA
        super().__init__(template_path)

        # add language to environment
        self.env.extend(language=language)

        # use texescape as escape filter
        self.env.filters['e'] = rst.escape
        self.env.filters['escape'] = rst.escape
        self.env.filters['heading'] = rst.heading