    def load(self, name, id):
        """Loads and sets this items's attributes from the item.db database. The item is looked up
        in the database by name or id.

        :param name: The name of the item to look up in the monster.item database.
        :param id: The id of the item to look up in the item.db database.

        :type name: String
        :type id: Integer

        :rtype: None
        :returns: None

        **Examples:**

        >>> potion_item = Item()
        >>> potion_item.load("Potion", None)    # Load an item by name.
        >>> potion_item.load(None, 1)           # Load an item by id.
        >>> pprint.pprint(potion_item.__dict__)
        {'description': u'Heals a monster by 50 HP.',
         'effect': [u'heal'],
         'id': 1,
         'name': u'Potion',
         'power': 50,
         'type': u'Consumable'}

        """

        if name:
            results = items.lookup(name, table="item")
        elif id:
            results = items.lookup_by_id(id, table="item")

        self.name = results["name"]
        self.name_trans = trans(results["name_trans"])
        self.description = results["description"]
        self.description_trans = trans(results["description_trans"])

        self.id = results["id"]
        self.type = results["type"]
        self.power = results["power"]
        self.sprite = results["sprite"]
        self.usable_in = results["usable_in"]
        self.surface = tools.load_and_scale(self.sprite)
        self.surface_size_original = self.surface.get_size()

        #TODO: maybe break out into own function
        from operator import itemgetter
        self.target = map(itemgetter(0), filter(itemgetter(1),
                          sorted(results["target"].items(), key=itemgetter(1), reverse=True)))

        self.effect = results["effects"]