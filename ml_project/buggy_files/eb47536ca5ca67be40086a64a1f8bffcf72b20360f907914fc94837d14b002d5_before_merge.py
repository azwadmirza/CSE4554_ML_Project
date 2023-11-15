        def swap_it(menuitem):
            monster = menuitem.game_object
            trans = translator.translate
            if monster in self.game.get_state_name('CombatState').active_monsters:
                tools.open_dialog(self.game, [trans('combat_isactive', {"name": monster.name})])
                return
            elif monster.current_hp < 1:
                tools.open_dialog(self.game, [trans('combat_fainted', {"name": monster.name})])
            player = self.game.player1
            target = player.monsters[0]
            swap = Technique("Swap")
            swap.other = monster
            combat_state = self.game.get_state_name("CombatState")
            combat_state.enqueue_action(player, swap, target)
            self.game.pop_state()  # close technique menu
            self.game.pop_state()  # close the monster action menu