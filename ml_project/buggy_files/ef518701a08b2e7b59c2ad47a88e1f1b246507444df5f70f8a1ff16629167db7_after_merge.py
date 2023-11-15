    def _actor_table(self, actor_id):
        """Fetch and parse the actor table information for a single actor ID.

        Args:
            actor_id: A actor ID to get information about.

        Returns:
            A dictionary with information about the actor ID in question.
        """
        assert isinstance(actor_id, ray.ActorID)
        message = self.redis_client.execute_command(
            "RAY.TABLE_LOOKUP", gcs_utils.TablePrefix.Value("ACTOR"), "",
            actor_id.binary())
        if message is None:
            return {}
        gcs_entries = gcs_utils.GcsEntry.FromString(message)

        assert len(gcs_entries.entries) > 0
        actor_table_data = gcs_utils.ActorTableData.FromString(
            gcs_entries.entries[-1])

        actor_info = {
            "ActorID": binary_to_hex(actor_table_data.actor_id),
            "JobID": binary_to_hex(actor_table_data.job_id),
            "Address": {
                "IPAddress": actor_table_data.address.ip_address,
                "Port": actor_table_data.address.port
            },
            "OwnerAddress": {
                "IPAddress": actor_table_data.owner_address.ip_address,
                "Port": actor_table_data.owner_address.port
            },
            "IsDirectCall": actor_table_data.is_direct_call,
            "State": actor_table_data.state,
            "Timestamp": actor_table_data.timestamp,
        }

        return actor_info