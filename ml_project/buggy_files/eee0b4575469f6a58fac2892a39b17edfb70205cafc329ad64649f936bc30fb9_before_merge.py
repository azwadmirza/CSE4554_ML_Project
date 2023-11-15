    def lookup(self, name, table="monster"):
        """Looks up a monster, technique, item, or npc based on name or id.

        :param name: The name of the monster, technique, item, or npc.
        :param table: Which index to do the search in. Can be: "monster",
            "item", "npc", or "technique".
        :type name: String
        :type table: String

        :rtype: Dict
        :returns: A dictionary from the resulting lookup.

        """
        if name in self.database[table]:
            return self.database[table][name]

        for id, item in self.database[table].items():
            if item['name'] == name:
                return item