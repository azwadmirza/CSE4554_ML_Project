    def send_msg(self, msg: Dict[str, Any]) -> None:
        """ Send a message to telegram channel """
        try:

            if msg['type'] == RPCMessageType.BUY_NOTIFICATION:
                valuedict = self._config['webhook'].get('webhookbuy', None)
            elif msg['type'] == RPCMessageType.SELL_NOTIFICATION:
                valuedict = self._config['webhook'].get('webhooksell', None)
            elif msg['type'] in(RPCMessageType.STATUS_NOTIFICATION,
                                RPCMessageType.CUSTOM_NOTIFICATION,
                                RPCMessageType.WARNING_NOTIFICATION):
                valuedict = self._config['webhook'].get('webhookstatus', None)
            else:
                raise NotImplementedError('Unknown message type: {}'.format(msg['type']))
            if not valuedict:
                logger.info("Message type %s not configured for webhooks", msg['type'])
                return

            payload = {key: value.format(**msg) for (key, value) in valuedict.items()}
            self._send_msg(payload)
        except KeyError as exc:
            logger.exception("Problem calling Webhook. Please check your webhook configuration. "
                             "Exception: %s", exc)