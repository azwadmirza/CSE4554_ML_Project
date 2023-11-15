                def success(res):
                    msg = None
                    # it is possible this session has disconnected
                    # while authentication was taking place
                    if self._transport is None:
                        self.log.info(
                            "Client session disconnected during authentication",
                        )
                        return

                    if isinstance(res, types.Accept):
                        custom = {
                            u'x_cb_node_id': self._router_factory._node_id
                        }
                        welcome(res.realm, res.authid, res.authrole, res.authmethod, res.authprovider, res.authextra, custom)

                    elif isinstance(res, types.Deny):
                        msg = message.Abort(res.reason, res.message)

                    else:
                        pass

                    if msg:
                        self._transport.send(msg)