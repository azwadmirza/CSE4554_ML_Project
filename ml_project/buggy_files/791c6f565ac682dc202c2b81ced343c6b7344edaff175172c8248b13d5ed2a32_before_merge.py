    def _help(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /help.
        Show commands of the bot
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        forcebuy_text = "*/forcebuy <pair> [<rate>]:* `Instantly buys the given pair. " \
                        "Optionally takes a rate at which to buy.` \n"
        message = "*/start:* `Starts the trader`\n" \
                  "*/stop:* `Stops the trader`\n" \
                  "*/status [table]:* `Lists all open trades`\n" \
                  "         *table :* `will display trades in a table`\n" \
                  "*/profit:* `Lists cumulative profit from all finished trades`\n" \
                  "*/forcesell <trade_id>|all:* `Instantly sells the given trade or all trades, " \
                  "regardless of profit`\n" \
                  f"{forcebuy_text if self._config.get('forcebuy_enable', False) else '' }" \
                  "*/performance:* `Show performance of each finished trade grouped by pair`\n" \
                  "*/daily <n>:* `Shows profit or loss per day, over the last n days`\n" \
                  "*/count:* `Show number of trades running compared to allowed number of trades`" \
                  "\n" \
                  "*/balance:* `Show account balance per currency`\n" \
                  "*/stopbuy:* `Stops buying, but handles open trades gracefully` \n" \
                  "*/reload_conf:* `Reload configuration file` \n" \
                  "*/show_config:* `Show running configuration` \n" \
                  "*/whitelist:* `Show current whitelist` \n" \
                  "*/blacklist [pair]:* `Show current blacklist, or adds one or more pairs " \
                  "to the blacklist.` \n" \
                  "*/edge:* `Shows validated pairs by Edge if it is enabeld` \n" \
                  "*/help:* `This help message`\n" \
                  "*/version:* `Show version`"

        self._send_msg(message)