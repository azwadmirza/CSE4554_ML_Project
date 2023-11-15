    def indexentries(self, entries: Dict[str, List[Tuple[str, str, str, str, str]]]) -> None:
        warnings.warn('env.indexentries() is deprecated. Please use IndexDomain instead.',
                      RemovedInSphinx40Warning, stacklevel=2)
        from sphinx.domains.index import IndexDomain
        domain = cast(IndexDomain, self.get_domain('index'))
        domain.data['entries'] = entries