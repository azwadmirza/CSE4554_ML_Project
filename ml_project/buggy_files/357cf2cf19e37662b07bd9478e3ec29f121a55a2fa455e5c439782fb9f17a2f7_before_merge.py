    def received_token_balance(self, statistics):
        statistics = statistics["statistics"]
        if 'latest_block' in statistics:
            balance = (statistics["latest_block"]["transaction"]["total_up"] - \
                      statistics["latest_block"]["transaction"]["total_down"]) / 1024 / 1024
            self.token_balance_label.setText("%d" % balance)
        else:
            self.token_balance_label.setText("0")