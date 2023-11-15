    def use(self, user, target):
        """Applies this technique's effects as defined in the "effect" column of the technique
        database. This method will execute a function with the same name as the effect defined in
        the database. If you want to add a new effect, simply create a new function under the
        Technique class with the name of the effect you define in monster.db.

        :param user: The core.components.monster.Monster object that used this technique.
        :param target: The core.components.monter.Monster object that we are using this
            technique on.

        :type user: core.components.monster.Monster
        :type target: core.components.monster.Monster

        :rtype: bool
        :returns: If technique was successful or not

        **Examples:**

        >>> poison_tech = Technique("Poison Sting")
        >>> bulbatux.learn(poison_tech)
        >>>
        >>> bulbatux.moves[0].use(user=bulbatux, target=tuxmander)
        """
        # Loop through all the effects of this technique and execute the effect's function.
        # TODO: more robust API
        successful = False
        for effect in self.effect:
            if getattr(self, str(effect))(user, target):
                successful = True

        return successful