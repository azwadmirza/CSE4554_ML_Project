    def send_msg(self, msg: Dict[str, Any]) -> None:
        """ Send a message to telegram channel """

        if msg['type'] == RPCMessageType.BUY_NOTIFICATION:
            if self._fiat_converter:
                msg['stake_amount_fiat'] = self._fiat_converter.convert_amount(
                    msg['stake_amount'], msg['stake_currency'], msg['fiat_currency'])
            else:
                msg['stake_amount_fiat'] = 0

            message = ("*{exchange}:* Buying {pair}\n"
                       "at rate `{limit:.8f}\n"
                       "({stake_amount:.6f} {stake_currency}").format(**msg)

            if msg.get('fiat_currency', None):
                message += ",{stake_amount_fiat:.3f} {fiat_currency}".format(**msg)
            message += ")`"

        elif msg['type'] == RPCMessageType.SELL_NOTIFICATION:
            msg['amount'] = round(msg['amount'], 8)
            msg['profit_percent'] = round(msg['profit_percent'] * 100, 2)
            msg['duration'] = msg['close_date'].replace(
                microsecond=0) - msg['open_date'].replace(microsecond=0)
            msg['duration_min'] = msg['duration'].total_seconds() / 60

            message = ("*{exchange}:* Selling {pair}\n"
                       "*Rate:* `{limit:.8f}`\n"
                       "*Amount:* `{amount:.8f}`\n"
                       "*Open Rate:* `{open_rate:.8f}`\n"
                       "*Current Rate:* `{current_rate:.8f}`\n"
                       "*Sell Reason:* `{sell_reason}`\n"
                       "*Duration:* `{duration} ({duration_min:.1f} min)`\n"
                       "*Profit:* `{profit_percent:.2f}%`").format(**msg)

            # Check if all sell properties are available.
            # This might not be the case if the message origin is triggered by /forcesell
            if (all(prop in msg for prop in ['gain', 'fiat_currency', 'stake_currency'])
               and self._fiat_converter):
                msg['profit_fiat'] = self._fiat_converter.convert_amount(
                    msg['profit_amount'], msg['stake_currency'], msg['fiat_currency'])
                message += ('` ({gain}: {profit_amount:.8f} {stake_currency}`'
                            '` / {profit_fiat:.3f} {fiat_currency})`').format(**msg)

        elif msg['type'] == RPCMessageType.STATUS_NOTIFICATION:
            message = '*Status:* `{status}`'.format(**msg)

        elif msg['type'] == RPCMessageType.WARNING_NOTIFICATION:
            message = '*Warning:* `{status}`'.format(**msg)

        elif msg['type'] == RPCMessageType.CUSTOM_NOTIFICATION:
            message = '{status}'.format(**msg)

        else:
            raise NotImplementedError('Unknown message type: {}'.format(msg['type']))

        self._send_msg(message)