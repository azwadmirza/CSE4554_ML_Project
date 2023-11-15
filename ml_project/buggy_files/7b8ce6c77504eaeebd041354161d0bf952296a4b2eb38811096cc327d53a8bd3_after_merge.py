    def received_trustchain_statistics(self, statistics):
        if not statistics:
            return
        statistics = statistics["statistics"]
        self.public_key = statistics["id"]
        total_up = 0
        total_down = 0
        if 'latest_block' in statistics:
            total_up = statistics["latest_block"]["transaction"]["total_up"]
            total_down = statistics["latest_block"]["transaction"]["total_down"]

        self.window().trust_contribution_amount_label.setText("%s MBytes" % (total_up / self.byte_scale))
        self.window().trust_consumption_amount_label.setText("%s MBytes" % (total_down / self.byte_scale))

        self.window().trust_people_helped_label.setText("%d" % statistics["peers_that_pk_helped"])
        self.window().trust_people_helped_you_label.setText("%d" % statistics["peers_that_helped_pk"])