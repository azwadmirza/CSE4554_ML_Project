    def on_total_count_results(self, response):
        # Workaround for possible race condition between simultaneous requests. Sees query_total_count for details.
        if response and "total" in response:
            self.count_query_complete.emit(response)
            self.model.total_items = response['total']
            # TODO unify this label update with the above count_query_complete signal
            if self.num_results_label:
                self.num_results_label.setText("%d results" % self.model.total_items)
            return False