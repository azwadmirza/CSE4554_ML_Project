    def send_to_azure_queue(self, queue_uri, message, session):
        queue_service, queue_name = StorageUtilities.get_queue_client_by_uri(queue_uri, session)
        return StorageUtilities.put_queue_message(queue_service, queue_name, self.pack(message)).id