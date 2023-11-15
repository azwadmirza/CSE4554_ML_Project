    async def train_parsers(self, skills):
        """Train the parsers.

        Args:
            skills (list): A list of all the loaded skills.

        """
        if "parsers" in self.modules:
            parsers = self.modules.get("parsers", {})
            rasanlu = get_parser_config("rasanlu", parsers)
            if rasanlu and rasanlu["enabled"]:
                await train_rasanlu(rasanlu, skills)