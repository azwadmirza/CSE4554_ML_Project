    def _parse_template_parameter_list(self) -> ASTTemplateParams:
        # only: '<' parameter-list '>'
        # we assume that 'template' has just been parsed
        templateParams = []  # type: List[ASTTemplateParam]
        self.skip_ws()
        if not self.skip_string("<"):
            self.fail("Expected '<' after 'template'")
        while 1:
            pos = self.pos
            err = None
            try:
                param = self._parse_template_paramter()
                templateParams.append(param)
            except DefinitionError as eParam:
                self.pos = pos
                err = eParam
            self.skip_ws()
            if self.skip_string('>'):
                return ASTTemplateParams(templateParams)
            elif self.skip_string(','):
                continue
            else:
                header = "Error in template parameter list."
                errs = []
                if err:
                    errs.append((err, "If parameter"))
                try:
                    self.fail('Expected "," or ">".')
                except DefinitionError as e:
                    errs.append((e, "If no parameter"))
                print(errs)
                raise self._make_multi_error(errs, header)