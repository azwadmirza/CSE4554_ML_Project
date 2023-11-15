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