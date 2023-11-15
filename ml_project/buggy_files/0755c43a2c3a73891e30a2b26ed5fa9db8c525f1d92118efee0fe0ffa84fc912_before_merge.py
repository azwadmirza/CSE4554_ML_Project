    def get_hypothesis_conversions(self, location: str) -> Optional[Callable]:
        definitions = [item for item in self.definition.raw.get("parameters", []) if item["in"] == location]
        if definitions:
            return self.schema.get_hypothesis_conversion(definitions)
        return None