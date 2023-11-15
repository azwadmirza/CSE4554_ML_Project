    def _parse_template_parameter_list(self) -> ASTTemplateParams:
        # only: '<' parameter-list '>'
        # we assume that 'template' has just been parsed
        templateParams = []  # type: List[ASTTemplateParam]
        self.skip_ws()
        if not self.skip_string("<"):
            self.fail("Expected '<' after 'template'")
        prevErrors = []
        while 1:
            self.skip_ws()
            if self.skip_word('template'):
                # declare a tenplate template parameter
                nestedParams = self._parse_template_parameter_list()
            else:
                nestedParams = None
            self.skip_ws()
            key = None
            if self.skip_word_and_ws('typename'):
                key = 'typename'
            elif self.skip_word_and_ws('class'):
                key = 'class'
            elif nestedParams:
                self.fail("Expected 'typename' or 'class' after "
                          "template template parameter list.")
            if key:
                # declare a type or template type parameter
                self.skip_ws()
                parameterPack = self.skip_string('...')
                self.skip_ws()
                if self.match(identifier_re):
                    identifier = ASTIdentifier(self.matched_text)
                else:
                    identifier = None
                self.skip_ws()
                if not parameterPack and self.skip_string('='):
                    default = self._parse_type(named=False, outer=None)
                else:
                    default = None
                data = ASTTemplateKeyParamPackIdDefault(key, identifier,
                                                        parameterPack, default)
                if nestedParams:
                    # template type
                    templateParams.append(
                        ASTTemplateParamTemplateType(nestedParams, data))
                else:
                    # type
                    templateParams.append(ASTTemplateParamType(data))
            else:
                # declare a non-type parameter, or constrained type parameter
                pos = self.pos
                try:
                    param = self._parse_type_with_init('maybe', 'templateParam')
                    templateParams.append(ASTTemplateParamNonType(param))
                except DefinitionError as e:
                    msg = "If non-type template parameter or constrained template parameter"
                    prevErrors.append((e, msg))
                    self.pos = pos
            self.skip_ws()
            if self.skip_string('>'):
                return ASTTemplateParams(templateParams)
            elif self.skip_string(','):
                prevErrors = []
                continue
            else:
                header = "Error in template parameter list."
                try:
                    self.fail('Expected "=", ",", or ">".')
                except DefinitionError as e:
                    prevErrors.append((e, ""))
                raise self._make_multi_error(prevErrors, header)