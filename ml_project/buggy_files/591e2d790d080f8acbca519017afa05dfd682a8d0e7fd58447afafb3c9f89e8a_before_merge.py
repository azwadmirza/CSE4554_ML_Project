    def update_labels(self, dirty=False):

        folder = self.model.channel_info.get("type", None) == COLLECTION_NODE
        personal = self.model.channel_info.get("state", None) == "Personal"
        root = len(self.channels_stack) == 1
        legacy = self.model.channel_info.get("state", None) == "Legacy"
        complete = self.model.channel_info.get("state", None) == "Complete"
        search = isinstance(self.model, SearchResultsModel)
        discovered = isinstance(self.model, DiscoveredChannelsModel)
        personal_model = isinstance(self.model, PersonalChannelsModel)

        self.category_selector.setHidden(root and (discovered or personal_model))
        # initialize the channel page

        # Assemble the channels navigation breadcrumb by utilising RichText links feature
        self.channel_name_label.setTextFormat(Qt.RichText)
        # We build the breadcrumb text backwards, by performing lookahead on each step.
        # While building the breadcrumb label in RichText we also assemble an undecorated variant of the same text
        # to estimate if we need to elide the breadcrumb. We cannot use RichText contents directly with
        # .elidedText method because QT will elide the tags as well.
        breadcrumb_text = ''
        breadcrumb_text_undecorated = ''
        path_parts = [(m, model.channel_info["name"]) for m, model in enumerate(self.channels_stack)]
        slash_separator = '<font color=#A5A5A5>  /  </font>'
        for m, channel_name in reversed(path_parts):
            breadcrumb_text_undecorated = " / " + channel_name + breadcrumb_text_undecorated
            breadcrumb_text_elided = self.channel_name_label.fontMetrics().elidedText(
                breadcrumb_text_undecorated, 0, self.channel_name_label.width()
            )
            must_elide = breadcrumb_text_undecorated != breadcrumb_text_elided
            if must_elide:
                channel_name = "..."
            breadcrumb_text = (
                slash_separator
                + f'<a style="text-decoration:none;color:#A5A5A5;" href="{m}">{channel_name}</a>'
                + breadcrumb_text
            )
            if must_elide:
                break
        # Remove the leftmost slash:
        if len(breadcrumb_text) >= len(slash_separator):
            breadcrumb_text = breadcrumb_text[len(slash_separator) :]

        self.new_channel_button.setText("NEW CHANNEL" if root else "NEW FOLDER")

        self.channel_name_label.setText(breadcrumb_text)
        self.channel_name_label.setTextInteractionFlags(Qt.TextBrowserInteraction)

        self.channel_back_button.setHidden(root)
        self.channel_options_button.setHidden(not personal or root)
        self.new_channel_button.setHidden(not personal)

        self.channel_state_label.setText(self.model.channel_info.get("state", "This text should not ever be shown"))

        self.subscription_widget.setHidden(root or personal or folder)
        if not self.subscription_widget.isHidden():
            self.subscription_widget.update_subscribe_button(self.model.channel_info)

        self.channel_preview_button.setHidden((root and not search) or personal or legacy or complete)
        self.channel_state_label.setHidden(root or personal or complete)

        self.commit_control_bar.setHidden(self.autocommit_enabled or not dirty or not personal)

        if "total" in self.model.channel_info:
            if "torrents" in self.model.channel_info:
                self.channel_num_torrents_label.setText(
                    "{}/{} items".format(self.model.channel_info["total"], self.model.channel_info["torrents"])
                )
            else:
                self.channel_num_torrents_label.setText("{} items".format(self.model.channel_info["total"]))