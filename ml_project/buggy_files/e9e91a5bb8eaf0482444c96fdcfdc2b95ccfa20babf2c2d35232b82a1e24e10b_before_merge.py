    def on_query_results(self, response, remote=False, on_top=False):
        """
        Updates the table with the response.
        :param response: List of the items to be added to the model
        :param remote: True if response is from a remote peer. Default: False
        :param on_top: True if items should be added at the top of the list
        :return: True, if response, False otherwise
        """
        # TODO: count remote results
        if not response:
            return False

        # Trigger labels update on the initial table load
        update_labels = len(self.data_items) == 0

        if not remote or (uuid.UUID(response.get('uuid')) in self.remote_queries):
            self.add_items(response['results'], on_top=remote or on_top)
            if "total" in response:
                self.channel_info["total"] = response["total"]
                update_labels = True
            elif remote and uuid.UUID(response.get('uuid')) == CHANNELS_VIEW_UUID:
                # This is a discovered channel (from a remote peer), update the total number of channels and the labels
                if self.channel_info.get("total"):
                    self.channel_info["total"] += len(response["results"])
                update_labels = True
            if update_labels:
                self.info_changed.emit(response['results'])
        return True