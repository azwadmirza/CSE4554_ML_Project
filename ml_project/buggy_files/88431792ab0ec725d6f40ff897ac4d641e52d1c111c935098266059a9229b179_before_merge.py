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

        if "parsers" in self.config:
            _LOGGER.debug(_("Processing parsers..."))
            parsers = self.config["parsers"] or {}

            dialogflow = parsers.get("dialogflow")
            if dialogflow and dialogflow["enabled"]:
                _LOGGER.debug(_("Checking dialogflow..."))
                ranked_skills += await parse_dialogflow(
                    self, skills, message, dialogflow
                )

            luisai = parsers.get("luisai")
            if luisai and luisai["enabled"]:
                _LOGGER.debug(_("Checking luisai..."))
                ranked_skills += await parse_luisai(self, skills, message, luisai)

            sapcai = parsers.get("sapcai")
            if sapcai and sapcai["enabled"]:
                _LOGGER.debug(_("Checking SAPCAI..."))
                ranked_skills += await parse_sapcai(self, skills, message, sapcai)

            witai = parsers.get("witai")
            if witai and witai["enabled"]:
                _LOGGER.debug(_("Checking wit.ai..."))
                ranked_skills += await parse_witai(self, skills, message, witai)

            watson = parsers.get("watson")
            if watson and watson["enabled"]:
                _LOGGER.debug(_("Checking IBM Watson..."))
                ranked_skills += await parse_watson(self, skills, message, watson)

            rasanlu = parsers.get("rasanlu")
            if rasanlu and rasanlu["enabled"]:
                _LOGGER.debug(_("Checking Rasa NLU..."))
                ranked_skills += await parse_rasanlu(self, skills, message, rasanlu)

        return sorted(ranked_skills, key=lambda k: k["score"], reverse=True)