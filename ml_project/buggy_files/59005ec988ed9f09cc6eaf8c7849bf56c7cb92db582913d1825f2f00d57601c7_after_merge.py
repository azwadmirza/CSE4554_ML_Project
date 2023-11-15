    async def get_ranked_skills(self, message):
        """Take a message and return a ranked list of matching skills."""
        skills = []
        skills = skills + await parse_regex(self, message)

        if "parsers" in self.config:
            _LOGGER.debug("Processing parsers...")
            parsers = self.config["parsers"] or []

            dialogflow = [p for p in parsers if p["name"] == "dialogflow"
                          or p["name"] == "apiai"]

            # Show deprecation message but  parse message
            # Once it stops working remove this bit
            apiai = [p for p in parsers if p["name"] == "apiai"]
            if apiai:
                _LOGGER.warning("Api.ai is now called Dialogflow. This "
                                "parser will stop working in the future "
                                "please swap: 'name: apiai' for "
                                "'name: dialogflow' in configuration.yaml")

            if len(dialogflow) == 1 and \
                    ("enabled" not in dialogflow[0] or
                     dialogflow[0]["enabled"] is not False):
                _LOGGER.debug("Checking dialogflow...")
                skills = skills + \
                    await parse_dialogflow(self, message, dialogflow[0])

            luisai = [p for p in parsers if p["name"] == "luisai"]
            if len(luisai) == 1 and \
                    ("enabled" not in luisai[0] or
                     luisai[0]["enabled"] is not False):
                _LOGGER.debug("Checking luisai...")
                skills = skills + \
                    await parse_luisai(self, message, luisai[0])

            recastai = [p for p in parsers if p["name"] == "recastai"]
            if len(recastai) == 1 and \
                    ("enabled" not in recastai[0] or
                     recastai[0]["enabled"] is not False):
                _LOGGER.debug("Checking Recast.AI...")
                skills = skills + \
                    await parse_recastai(self, message, recastai[0])

            witai = [p for p in parsers if p["name"] == "witai"]
            if len(witai) == 1 and \
                    ("enabled" not in witai[0] or
                     witai[0]["enabled"] is not False):
                _LOGGER.debug("Checking wit.ai...")
                skills = skills + \
                    await parse_witai(self, message, witai[0])

        return sorted(skills, key=lambda k: k["score"], reverse=True)