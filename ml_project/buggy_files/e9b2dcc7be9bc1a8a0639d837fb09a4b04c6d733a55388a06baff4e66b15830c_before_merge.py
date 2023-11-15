    def CountUsers(self):

        numusers = len(list(self.users.keys()))
        if numusers > 1:
            self.LabelPeople.show()
            self.LabelPeople.set_text(_("%i people in room") % numusers)
        elif numusers == 1:
            self.LabelPeople.show()
            self.LabelPeople.set_text(_("You are alone"))
        else:
            self.LabelPeople.hide()

        if self.room in self.roomsctrl.rooms:
            iter = self.roomsctrl.roomsmodel.get_iter_first()
            while iter:
                if self.roomsctrl.roomsmodel.get_value(iter, 0) == self.room:
                    self.roomsctrl.roomsmodel.set(iter, 1, numusers)
                    break
                iter = self.roomsctrl.roomsmodel.iter_next(iter)
        else:
            self.roomsctrl.roomsmodel.append([self.room, numusers, 0])
            self.roomsctrl.rooms.append(self.room)