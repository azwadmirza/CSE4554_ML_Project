    def heal(self, user, target):
        """This effect heals the target based on the item's power attribute.

        :param user: The monster or object that is using this item.
        :param target: The monster or object that we are using this item on.

        :type user: Varies
        :type target: Varies

        :rtype: bool
        :returns: Success

        **Examples:**
        >>> potion_item = Item("Potion")
        >>> potion_item.heal(bulbatux, game)
        """

        if target.current_hp == target.hp:
            return False
         # Heal the target monster by "self.power" number of hitpoints.
        target.current_hp += self.power

        # If we've exceeded the monster's maximum HP, set their health to 100% of their HP.
        if target.current_hp > target.hp:
            target.current_hp = target.hp

        return True