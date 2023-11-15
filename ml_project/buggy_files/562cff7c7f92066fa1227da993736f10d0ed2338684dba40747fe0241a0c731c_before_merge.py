    def load(self, name, id):
        """Loads and sets this technique's attributes from the technique
        database. The technique is looked up in the database by name or id.

        :param name: The name of the technique to look up in the monster
            database.
        :param id: The id of the technique to look up in the monster database.

        :type name: String
        :type id: Integer

        :rtype: None
        :returns: None

        **Examples:**

        >>>

        """

        if name:
            results = techniques.lookup(name, table="technique")
        elif id:
            results = techniques.database['technique'][id]

        self.name = results["name"]
        self.name_trans = trans(results["name_trans"])
        self.tech_id = results["id"]
        self.category = results["category"]
        self.icon = results["icon"]

        self._combat_counter = 0
        self._life_counter = 0

        self.type1 = results["types"][0]
        if len(results['types']) > 1:
            self.type2 = results["types"][1]
        else:
            self.type2 = None

        self.power = results["power"]
        self.effect = results["effects"]

        #TODO: maybe break out into own function
        from operator import itemgetter
        self.target = map(itemgetter(0), filter(itemgetter(1),
                          sorted(results["target"].items(), key=itemgetter(1), reverse=True)))

        # Load the animation sprites that will be used for this technique
        self.animation = results["animation"]
        self.images = []
        animation_dir = prepare.BASEDIR + "resources/animations/technique/"
        directory = sorted(os.listdir(animation_dir))
        for image in directory:
            if self.animation and image.startswith(self.animation):
                self.images.append("animations/technique/" + image)

        # Load the sound effect for this technique
        sfx_directory = "sounds/technique/"
        self.sfx = sfx_directory + results["sfx"]