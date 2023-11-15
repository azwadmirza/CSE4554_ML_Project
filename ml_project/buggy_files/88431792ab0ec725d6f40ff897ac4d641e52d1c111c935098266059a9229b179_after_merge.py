    async def get_ranked_skills(self, skills, message):
        """Take a message and return a ranked list of matching skills.

        Args:
            skills (list): List of all available skills.
            message (string): Context message to base the ranking of skills on.

        Returns:
            ranked_skills (list): List of all available skills sorted and ranked based on the score they muster when matched against the message parsed.

        """
        ranked_skills = []
        if isinstance(message, events.Message):
            ranked_skills += await parse_regex(self, skills, message)
            ranked_skills += await parse_format(self, skills, message)

        if "parsers" in self.modules:
            _LOGGER.debug(_("Processing parsers..."))
            parsers = self.modules.get("parsers", {})

            dialogflow = get_parser_config("dialogflow", parsers)
            if dialogflow and dialogflow["enabled"]:
                _LOGGER.debug(_("Checking dialogflow..."))
                ranked_skills += await parse_dialogflow(
                    self, skills, message, dialogflow
                )

            luisai = get_parser_config("luisai", parsers)
            if luisai and luisai["enabled"]:
                _LOGGER.debug(_("Checking luisai..."))
                ranked_skills += await parse_luisai(self, skills, message, luisai)

            sapcai = get_parser_config("sapcai", parsers)
            if sapcai and sapcai["enabled"]:
                _LOGGER.debug(_("Checking SAPCAI..."))
                ranked_skills += await parse_sapcai(self, skills, message, sapcai)

            witai = get_parser_config("witai", parsers)
            if witai and witai["enabled"]:
                _LOGGER.debug(_("Checking wit.ai..."))
                ranked_skills += await parse_witai(self, skills, message, witai)

            watson = get_parser_config("watson", parsers)
            if watson and watson["enabled"]:
                _LOGGER.debug(_("Checking IBM Watson..."))
                ranked_skills += await parse_watson(self, skills, message, watson)

            rasanlu = get_parser_config("rasanlu", parsers)
            if rasanlu and rasanlu["enabled"]:
                _LOGGER.debug(_("Checking Rasa NLU..."))
                ranked_skills += await parse_rasanlu(self, skills, message, rasanlu)

        return sorted(ranked_skills, key=lambda k: k["score"], reverse=True)