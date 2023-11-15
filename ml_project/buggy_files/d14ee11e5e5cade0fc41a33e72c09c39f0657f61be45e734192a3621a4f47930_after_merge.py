    def matchyaml(self, file: dict, text: str) -> List[MatchError]:
        matches: List[MatchError] = []
        if not self.matchplay:
            return matches

        yaml = ansiblelint.utils.parse_yaml_linenumbers(text, file['path'])
        # yaml returned can be an AnsibleUnicode (a string) when the yaml
        # file contains a single string. YAML spec allows this but we consider
        # this an fatal error.
        if isinstance(yaml, str):
            return [MatchError(
                filename=file['path'],
                rule=LoadingFailureRule()
            )]
        if not yaml:
            return matches

        if isinstance(yaml, dict):
            yaml = [yaml]

        yaml = ansiblelint.skip_utils.append_skipped_rules(yaml, text, file['type'])

        for play in yaml:

            # Bug #849
            if play is None:
                continue

            if self.id in play.get('skipped_rules', ()):
                continue

            result = self.matchplay(file, play)
            if not result:
                continue

            if isinstance(result, tuple):
                result = [result]

            if not isinstance(result, list):
                raise TypeError("{} is not a list".format(result))

            for section, message, *optional_linenumber in result:
                linenumber = self._matchplay_linenumber(play, optional_linenumber)
                matches.append(self.create_matcherror(
                    message=message,
                    linenumber=linenumber,
                    details=str(section),
                    filename=file['path']
                    ))
        return matches