    def namespace_popup_model(self):
        assert self.view
        model = Gio.Menu.new()

        part = Gio.Menu.new()
        part.append(gettext("_Open"), "tree-view.open")
        part.append(gettext("_Rename"), "tree-view.rename")
        model.append_section(None, part)

        part = Gio.Menu.new()
        part.append(gettext("New _Diagram"), "tree-view.create-diagram")
        part.append(gettext("New _Package"), "tree-view.create-package")
        model.append_section(None, part)

        part = Gio.Menu.new()
        part.append(gettext("De_lete"), "tree-view.delete")
        model.append_section(None, part)

        element = self.view.get_selected_element()

        part = Gio.Menu.new()
        for presentation in element.presentation:
            diagram = presentation.diagram
            menu_item = Gio.MenuItem.new(
                gettext('Show in "{diagram}"').format(diagram=diagram.name),
                "tree-view.show-in-diagram",
            )
            menu_item.set_attribute_value("target", GLib.Variant.new_string(diagram.id))
            part.append_item(menu_item)

            # Play it safe with an (arbitrary) upper bound
            if part.get_n_items() > 29:
                break

        if part.get_n_items() > 0:
            model.append_section(None, part)
        return model