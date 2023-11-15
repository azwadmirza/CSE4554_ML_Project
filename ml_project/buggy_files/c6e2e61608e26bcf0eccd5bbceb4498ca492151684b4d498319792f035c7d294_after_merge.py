    def check_party_hp(self):
        """ Apply status effects, then check HP, and party status

        * Monsters will be removed from play here

        :returns: None
        """
        for player in self.monsters_in_play.keys():
            for monster in self.monsters_in_play[player]:
                self.animate_hp(monster)
                if monster.current_hp <= 0 and not fainted(monster):
                    self.remove_monster_actions_from_queue(monster)
                    self.faint_monster(monster)