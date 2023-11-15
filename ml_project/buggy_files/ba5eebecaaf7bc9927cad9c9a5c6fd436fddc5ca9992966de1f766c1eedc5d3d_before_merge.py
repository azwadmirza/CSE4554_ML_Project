    async def train_parsers(self, skills):
        """Train the parsers.

        Args:
            skills (list): A list of all the loaded skills.

        """
        if "parsers" in self.config:
            parsers = self.config["parsers"] or {}
            rasanlu = parsers.get("rasanlu")
            if rasanlu and rasanlu["enabled"]:
                await train_rasanlu(rasanlu, skills)