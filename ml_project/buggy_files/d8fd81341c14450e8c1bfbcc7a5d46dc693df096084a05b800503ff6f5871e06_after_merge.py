    def initialize_with_channel_overview(self, overview):
        if not overview:
            return
        if 'error' in overview:
            self.window().edit_channel_stacked_widget.setCurrentIndex(0)
        else:
            if "mychannel" in overview:
                self.channel_overview = overview["mychannel"]
                self.set_editing_own_channel(True)
                self.window().edit_channel_name_label.setText("My channel")
            else:
                self.channel_overview = overview["channel"]
                self.set_editing_own_channel(False)
                self.window().edit_channel_name_label.setText(self.channel_overview["name"])

            self.window().edit_channel_overview_name_label.setText(self.channel_overview["name"])
            self.window().edit_channel_description_label.setText(self.channel_overview["description"])
            self.window().edit_channel_identifier_label.setText(self.channel_overview["identifier"])

            self.window().edit_channel_name_edit.setText(self.channel_overview["name"])
            self.window().edit_channel_description_edit.setText(self.channel_overview["description"])

            self.window().edit_channel_stacked_widget.setCurrentIndex(1)