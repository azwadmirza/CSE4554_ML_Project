    def append(self, imports: Union[Import, List[Import], None]) -> None:
        if imports:
            if isinstance(imports, Import):
                imports = [imports]
            for import_ in imports:
                if import_.import_.count('.') >= 1:
                    self[None].add(import_.import_)
                else:
                    self[import_.from_].add(import_.import_)
                    if import_.alias:
                        self.alias[import_.from_][import_.import_] = import_.alias