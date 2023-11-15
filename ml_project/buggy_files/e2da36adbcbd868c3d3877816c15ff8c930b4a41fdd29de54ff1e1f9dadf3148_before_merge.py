    def on_ipv8_community_stats(self, data):
        if not data:
            return
        self.window().communities_tree_widget.clear()
        for overlay in data["ipv8_overlay_statistics"]:
            item = QTreeWidgetItem(self.window().communities_tree_widget)
            item.setText(0, overlay["overlay_name"])
            item.setText(1, overlay["master_peer"][:6])
            item.setText(2, overlay["my_peer"][:6])
            item.setText(3, "%s" % len(overlay["peers"]))
            self.window().communities_tree_widget.addTopLevelItem(item)