    def startup_messages(self, config: Dict[str, Any], pairlist) -> None:
        if config['dry_run']:
            self.send_msg({
                'type': RPCMessageType.WARNING_NOTIFICATION,
                'status': 'Dry run is enabled. All trades are simulated.'
            })
        stake_currency = config['stake_currency']
        stake_amount = config['stake_amount']
        minimal_roi = config['minimal_roi']
        stoploss = config['stoploss']
        trailing_stop = config['trailing_stop']
        ticker_interval = config['ticker_interval']
        exchange_name = config['exchange']['name']
        strategy_name = config.get('strategy', '')
        self.send_msg({
            'type': RPCMessageType.CUSTOM_NOTIFICATION,
            'status': f'*Exchange:* `{exchange_name}`\n'
                      f'*Stake per trade:* `{stake_amount} {stake_currency}`\n'
                      f'*Minimum ROI:* `{minimal_roi}`\n'
                      f'*{"Trailing " if trailing_stop else ""}Stoploss:* `{stoploss}`\n'
                      f'*Ticker Interval:* `{ticker_interval}`\n'
                      f'*Strategy:* `{strategy_name}`'
        })
        self.send_msg({
            'type': RPCMessageType.STATUS_NOTIFICATION,
            'status': f'Searching for {stake_currency} pairs to buy and sell '
                      f'based on {pairlist.short_desc()}'
        })