    def open_technique_menu(self):
        """ Open menus to choose a Technique to use

        :return: None
        """

        def choose_technique():
            # open menu to choose technique
            menu = self.game.push_state("Menu")
            menu.shrink_to_items = True

            # add techniques to the menu
            for tech in self.monster.moves:
                image = self.shadow_text(tech.name)
                item = MenuItem(image, tech.name, None, tech)
                menu.add(item)

            # position the new menu
            menu.anchor("bottom", self.rect.top)
            menu.anchor("right", self.game.screen.get_rect().right)

            # set next menu after after selection is made
            menu.on_menu_selection = choose_target

        def choose_target(menu_item):
            # open menu to choose target of technique
            technique = menu_item.game_object
            state = self.game.push_state("CombatTargetMenuState")
            state.on_menu_selection = partial(enqueue_technique, technique)

        def enqueue_technique(technique, menu_item):
            # enqueue the technique
            target = menu_item.game_object
            combat_state = self.game.get_state_name("CombatState")
            combat_state.enqueue_action(self.monster, technique, target)

            # close all the open menus
            self.game.pop_state()  # close target chooser
            self.game.pop_state()  # close technique menu
            self.game.pop_state()  # close the monster action menu

        choose_technique()