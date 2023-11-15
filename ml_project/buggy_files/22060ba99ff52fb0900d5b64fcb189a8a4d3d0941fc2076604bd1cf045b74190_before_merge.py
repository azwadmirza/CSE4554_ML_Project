    def serve_forever(self, return_to_browser=False):
        """Main client loop."""

        exitkey = False

        while True and not exitkey:
            # Update the stats
            cs_status = self.update()

            # Update the screen
            exitkey = self.screen.update(self.stats,
                                         cs_status=cs_status,
                                         return_to_browser=return_to_browser)

        return self.get_mode()