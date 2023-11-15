    def poison(self, user, target):
        """This effect has a chance to apply the poison status effect to a target monster.
        Currently there is a 1/10 chance of poison.

        :param user: The core.components.monster.Monster object that used this technique.
        :param target: The core.components.monster.Monster object that we are using this
            technique on.

        :type user: core.components.monster.Monster
        :type target: core.components.monster.Monster

        :rtype: bool
        """
        already_poisoned = any(t for t in target.status if t.slug == "status_poison")

        if not already_poisoned and random.randrange(1, 2) == 1:
            target.apply_status(Technique("status_poison"))
            return True

        return False