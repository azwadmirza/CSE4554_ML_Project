    def on_menu_selection(self, menu_item):
        """ Called when player has selected something from the inventory

        Currently, opens a new menu depending on the state context

        :param menu_item:
        :return:
        """
        item = menu_item.game_object
        state = self.determine_state_called_from()

        if state in item.usable_in:
            self.open_confirm_use_menu(item)
        else:
            msg = trans('item_cannot_use_here', {'name': item.name_trans})
            tools.open_dialog(self.game, [msg])