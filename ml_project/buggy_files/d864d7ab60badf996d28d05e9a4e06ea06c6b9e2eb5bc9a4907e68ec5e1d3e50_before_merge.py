    def __add_tag(self, activator, model, library):
        add = AddTagDialog(self, self.__songinfo.can_change(), library)

        while True:
            resp = add.run()
            if resp != Gtk.ResponseType.OK:
                break
            tag = add.get_tag()
            value = add.get_value()
            assert isinstance(value, unicode)
            if tag in massagers.tags:
                value = massagers.tags[tag].validate(value)
            if not self.__songinfo.can_change(tag):
                title = _("Invalid tag")
                msg = _("Invalid tag <b>%s</b>\n\nThe files currently"
                        " selected do not support editing this tag."
                        ) % util.escape(tag)
                qltk.ErrorMessage(self, title, msg).run()
            else:
                self.__add_new_tag(model, tag, value)
                break

        add.destroy()