    def _on_selection_changed(self, selected, deselected):
        selected_indices = self.table_view.selectedIndexes()
        if not selected_indices:
            self.table_view.clearSelection()
            return

        data_item = selected_indices[-1].model().data_items[selected_indices[-1].row()]
        if not dict_item_is_any_of(data_item, 'type', [REGULAR_TORRENT]):
            return

        # Trigger health check if necessary
        # When the user scrolls the list, we only want to trigger health checks on the line
        # that the user stopped on, so we do not generate excessive health checks.
        if data_item['last_tracker_check'] == 0 and data_item.get(u'health') != HEALTH_CHECKING:
            if self.healthcheck_cooldown.isActive():
                self.healthcheck_cooldown.stop()
            else:
                self.check_torrent_health(data_item)
            self.healthcheck_cooldown.start(HEALTHCHECK_DELAY_MS)