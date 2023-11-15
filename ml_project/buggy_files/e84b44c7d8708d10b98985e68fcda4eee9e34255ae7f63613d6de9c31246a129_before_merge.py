    def open_swap_menu(self):
        """ Open menus to swap monsters in party

        :return: None
        """

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

        menu = self.game.push_state("MonsterMenuState")
        menu.on_menu_selection = swap_it
        menu.anchor("bottom", self.rect.top)
        menu.anchor("right", self.game.screen.get_rect().right)
        menu.monster = self.monster