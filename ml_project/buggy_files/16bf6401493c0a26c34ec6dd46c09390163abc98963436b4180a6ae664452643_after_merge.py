    def update_results(self):
        scores = [mk if isinstance(mk, str) else silhouette_score(
            self.preproces(self.data).X, mk.labels) for mk in (
                self.clusterings[k] for k in range(self.k_from, self.k_to + 1))]
        best_row = max(
            range(len(scores)), default=0,
            key=lambda x: 0 if isinstance(scores[x], str) else scores[x]
        )
        self.table_model.set_scores(scores, self.k_from)
        self.table_view.selectRow(best_row)
        self.table_view.setFocus(Qt.OtherFocusReason)
        self.table_view.resizeRowsToContents()