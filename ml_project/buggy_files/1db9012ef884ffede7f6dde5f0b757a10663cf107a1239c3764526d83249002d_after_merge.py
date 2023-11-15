    def load(self, slug, id):
        """Loads and sets this items's attributes from the item.db database. The item is looked up
        in the database by name or id.

        :param slug: The item slug to look up in the monster.item database.
        :param id: The id of the item to look up in the item.db database.

        :type slug: String
        :type id: Integer

        :rtype: None
        :returns: None

        **Examples:**

        >>> potion_item = Item()
        >>> potion_item.load("item_potion", None)    # Load an item by name.
        >>> potion_item.load(None, 1)           # Load an item by id.
        >>> pprint.pprint(potion_item.__dict__)
        {'description': u'Heals a monster by 50 HP.',
         'effect': [u'heal'],
         'id': 1,
         'name': u'Potion',
         'power': 50,
         'type': u'Consumable'}

        """

        if slug:
            results = items.lookup(slug, table="item")
        elif id:
            results = items.lookup_by_id(id, table="item")
        else:
            # TODO: some kind of useful message here
            raise RuntimeError

        self.slug = results["slug"]                             # short English identifier
        self.name = trans(results["name_trans"])                # will be locale string
        self.description = trans(results["description_trans"])  # will be locale string

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