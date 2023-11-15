    def recent_events(self, events):
        if self.search_task:
            recent = [d for d in self.search_task.fetch()]
            if recent:
                currently_avail = [rec['source'] for rec in self.available_exports]
                self.available_exports.extend([{'source': rec, 'selected': True} for rec in recent if rec not in currently_avail])
                self._update_avail_recs_menu()
            if self.search_task.completed:
                self.search_task = None
                self.search_button.outer_label = ''
                self.search_button.label = 'Search'