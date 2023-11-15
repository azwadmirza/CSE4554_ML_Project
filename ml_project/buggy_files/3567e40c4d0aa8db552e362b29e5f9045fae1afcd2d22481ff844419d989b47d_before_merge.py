    def faint(self, user, target):
        """ Faint this monster.  Typically, called by combat to faint self, not others.

        :param user: The core.components.monster.Monster object that used this technique.
        :param target: The core.components.monster.Monster object that we are using this
            technique on.

        :type user: core.components.monster.Monster
        :type target: core.components.monster.Monster

        :rtype: bool
        """
        already_fainted = any(t for t in target.status if t.name == "Faint")

        if already_fainted:
            raise RuntimeError
        else:
            target.apply_status(Technique("Faint"))
            return True