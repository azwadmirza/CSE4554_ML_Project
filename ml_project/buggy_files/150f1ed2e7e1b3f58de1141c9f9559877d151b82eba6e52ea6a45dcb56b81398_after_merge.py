    def __init__(self, parent):
        HomePanel.__init__(self, parent, 'Recent Activity', SEPARATOR_GREY, (1, 0))
        session = self.utility.session
        # TODO(emilon): This observer should be removed when shutting down.
        session.add_observer(self.on_tunnel_remove, NTFY_TUNNEL, [NTFY_REMOVE])