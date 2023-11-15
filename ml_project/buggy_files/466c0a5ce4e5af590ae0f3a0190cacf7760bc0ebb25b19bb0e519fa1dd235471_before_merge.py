    async def parse(self, message):
        """Parse a string against all skills."""
        self.stats["messages_parsed"] = self.stats["messages_parsed"] + 1
        tasks = []
        if message is not None and message.text.strip() != "":
            _LOGGER.debug(_("Parsing input: %s"), message.text)

            tasks.append(
                self.eventloop.create_task(parse_always(self, message)))

            unconstrained_skills = await self._constrain_skills(
                self.skills, message)
            ranked_skills = await self.get_ranked_skills(
                unconstrained_skills, message)
            if ranked_skills:
                tasks.append(
                    self.eventloop.create_task(
                        self.run_skill(ranked_skills[0]["skill"],
                                       ranked_skills[0]["config"],
                                       message)))

        return tasks