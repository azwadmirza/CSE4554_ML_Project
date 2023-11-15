    def lookup(self, slug, table="monster"):
        """Looks up a monster, technique, item, or npc based on name or id.

        :param slug: The slug of the monster, technique, item, or npc.  A short English identifier.
        :param table: Which index to do the search in. Can be: "monster",
            "item", "npc", or "technique".
        :type slug: String
        :type table: String

        :rtype: Dict
        :returns: A dictionary from the resulting lookup.

        """
        if slug in self.database[table]:
            return self.database[table][slug]

        for id, item in self.database[table].items():
            # TODO: localize *everything*
            # the slug lookup will fail for monsters and npc's
            # eventually, we may want to localize monster names or npc
            # in that case, all DB objects will have a slug
            # for now, we silently fail and lookup by name instead
            try:
                if item['slug'] == slug:
                    return item
            except KeyError:
                if item['name'] == slug:
                    return item