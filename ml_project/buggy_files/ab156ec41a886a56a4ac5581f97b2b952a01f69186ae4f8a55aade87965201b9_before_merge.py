    def right_menu(self, evt):
        menu = wx.Menu()
        all_menu = wx.Menu()

        unsorted_choices = [
            (name, annotation, num, is_input_module, identifier)
            for (name, annotation, num, is_input_module), identifier in
            zip(self.orig_choices, self.IDs)]
        fn_key = lambda x: (x[2], x)
        choices_sorted_by_num = sorted(unsorted_choices, key=fn_key)
        for name, annotation, num, is_input_module, choiceid in \
                choices_sorted_by_num:
            all_menu.Append(choiceid, "filler")

        align_twosided_items(
                self.combo_dlg,
                all_menu.MenuItems,
                left_texts=[name for name, _, _, _, _ in choices_sorted_by_num],
                right_texts=[self.get_choice_label(choice)
                             for choice in choices_sorted_by_num])

        submenus = {}
        for name, annotation, num, is_input_module, choiceid \
                in choices_sorted_by_num:
            if not annotation:
                continue
            key = (num, annotation, is_input_module)
            if key not in submenus:
                submenus[key] = wx.Menu()
            submenus[key].Append(choiceid, name)
        menu.AppendMenu(wx.ID_ANY, "All", all_menu)
        sorted_submenus = sorted(submenus.items())
        for (num, annotation, is_input_module), submenu in sorted_submenus:
            menu.AppendMenu(wx.ID_ANY, "filler", submenu)
        align_twosided_items(
                self.combo_dlg,
                menu.MenuItems,
                left_texts=['All'] + [k[1] for k, v in sorted_submenus],
                right_texts=[''] + [
                    "  " if is_input_module else "#%02d" % num
                    for (num, annotation, is_input_module), v
                    in sorted_submenus])
        self.PopupMenu(menu)
        menu.Destroy()