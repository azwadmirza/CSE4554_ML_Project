    def __Suffix_Verb_Step2a(self, token):
        for suffix in self.__suffix_verb_step2a:
            if token.endswith(suffix):
                if suffix == '\u062a' and len(token) >= 4:
                    token = token[:-1]
                    self.suffix_verb_step2a_success = True
                    break

                if suffix in self.__conjugation_suffix_verb_4 and len(token) >= 4:
                    token = token[:-1]
                    self.suffix_verb_step2a_success = True
                    break

                if suffix in self.__conjugation_suffix_verb_past and len(token) >= 5:
                    token = token[:-2]  # past
                    self.suffix_verb_step2a_success = True
                    break

                if suffix in self.__conjugation_suffix_verb_present and len(token) > 5:
                    token = token[:-2]  # present
                    self.suffix_verb_step2a_success = True
                    break

                if suffix == '\u062a\u0645\u0627' and len(token) >= 6:
                    token = token[:-3]
                    self.suffix_verb_step2a_success = True
                    break
        return  token