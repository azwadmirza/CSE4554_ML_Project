    def get_requirement(self):
        try:
            req = first(requirements.parse("{0}{1}".format(self.name, self.version)))
        except RequirementParseError:
            raise RequirementError(
                "Error parsing requirement: %s%s" % (self.name, self.version)
            )
        return req