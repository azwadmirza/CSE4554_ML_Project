    def Display(self, item):

        if item not in self.data:
            return

        if not self.Search:
            self.Immediate.hide()
            self.Position.hide()
            self.Country.hide()
            self.Queue.hide()
            self.Immediate.hide()
            self.ImmediateLabel.hide()
            self.PositionLabel.hide()
            self.QueueLabel.hide()
            self.ImmediateLabel.hide()
            self.DownloadItem.hide()
            self.DownloadAll.hide()
        else:
            self.Immediate.show()
            self.Position.show()
            self.Country.show()
            self.Queue.show()
            self.Immediate.show()
            self.ImmediateLabel.show()
            self.PositionLabel.show()
            self.QueueLabel.show()
            self.ImmediateLabel.show()
            self.DownloadItem.show()
            self.DownloadAll.show()

        self.current = item
        data = self.data[self.current]
        More = False

        if len(list(self.data.keys())) > 1:
            More = True

        self.Next.set_sensitive(More)
        self.Previous.set_sensitive(More)
        self.DownloadAll.set_sensitive(More)

        self.Username.set_text(data["user"])
        self.Filename.set_text(data["filename"])
        self.Directory.set_text(data["directory"])
        self.Size.set_text(str(data["size"]))
        self.Speed.set_text(data["speed"])
        self.Position.set_text(str(data["position"]))

        if data["bitrate"] not in ("", None):
            self.Bitrate.set_text(data["bitrate"])
        else:
            self.Bitrate.set_text("")

        self.Length.set_text(data["length"])
        self.Queue.set_text(data["queue"])
        self.Immediate.set_text(str(data["immediate"] == "Y"))

        country = data["country"]
        if country not in ("", None):
            self.Country.set_markup(_("<b>Country Code:</b> ") + country)
            self.Country.show()
        else:
            self.Country.set_text("")
            self.Country.hide()