    def on_update_menu(self, event, menu):
        import wx
        assert isinstance(menu, wx.Menu)
        menu_items = list(menu.GetMenuItems())
        breaks = ((self.MI_IMAGES, self.__images),
                  (self.MI_OBJECTS, self.__objects),
                  (self.MI_MASKS, self.__masks))
        for start, item in enumerate(menu_items):
            assert isinstance(item, wx.MenuItem)
            if item.Label == self.MI_INTERPOLATION:
                break
        else:
            return
        window = self.__get_window_from_event(event)
        idx = start + 1
        if menu_items[idx].IsSeparator():
            idx += 1
        label_fmt = "--- %s ---"
        for key, sequence in breaks:
            label = label_fmt % key
            if idx >= len(menu_items) or menu_items[idx].Text != label:
                item = menu.Insert(idx, wx.NewId(), label)
                item.Enable(False)
                menu_items.insert(idx, item)
            idx += 1
            #
            # Pair data items with menu items
            #
            for data in sequence:
                name = data.name
                if idx == len(menu_items) or\
                   menu_items[idx].Text.startswith("---") or\
                   menu_items[idx].IsSeparator():
                    sub_menu = wx.Menu()
                    my_id =  wx.NewId()
                    sub_menu_item = menu.InsertMenu(
                        idx, my_id, name, sub_menu)
                    if data.mode == MODE_HIDE:
                        sub_menu_item.Enable(False)
                    menu_items.insert(idx, sub_menu_item)
                    self.__initialize_sub_menu(event, sub_menu, data)
                    def on_update_ui(event, sub_menu = sub_menu, data=data):
                        self.__update_sub_menu(event, sub_menu, data)
                    window.Bind(
                        wx.EVT_UPDATE_UI, on_update_ui, id = my_id)
                    idx += 1
                else:
                    self.__update_sub_menu(
                        menu_items[idx], menu_items[idx].GetMenu(), data)
                    idx += 1
            #
            # Remove excess menu items
            #
            while len(menu_items) < idx and menu_items[idx].IsEnabled():
                menu.RemoveItem(item)
                del menu_items[idx]