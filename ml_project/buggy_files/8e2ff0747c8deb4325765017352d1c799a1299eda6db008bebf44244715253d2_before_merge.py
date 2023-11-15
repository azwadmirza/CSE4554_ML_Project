    def _query(self, config_name: Optional[str], line: str) -> List[str]:
        from .._internal.utils import get_args

        new_word = len(line) == 0 or line[-1] == " "
        parsed_args = get_args(line.split())
        words = parsed_args.overrides
        if new_word or len(words) == 0:
            word = ""
        else:
            word = words[-1]
            words = words[0:-1]

        run_mode = RunMode.MULTIRUN if parsed_args.multirun else RunMode.RUN
        config = self.config_loader.load_configuration(
            config_name=config_name, overrides=words, run_mode=run_mode
        )

        fname_prefix, filename = CompletionPlugin._get_filename(word)
        if filename is not None:
            assert fname_prefix is not None
            result = CompletionPlugin.complete_files(filename)
            result = [fname_prefix + file for file in result]
        else:
            matched_groups, exact_match = self._query_config_groups(word)
            config_matches: List[str] = []
            if not exact_match:
                config_matches = CompletionPlugin._get_matches(config, word)
            result = list(set(matched_groups + config_matches))

        return sorted(result)