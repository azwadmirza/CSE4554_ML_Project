    def send_to_azure_queue(self, queue_uri, message, session):
        try:
            queue_service, queue_name = StorageUtilities.get_queue_client_by_uri(queue_uri, session)
            return StorageUtilities.put_queue_message(
                queue_service,
                queue_name,
                self.pack(message)).id
        except AzureHttpError as e:
            if e.status_code == 403:
                self.log.error("Access Error - Storage Queue Data Contributor Role is required "
                               "to enqueue messages to the Azure Queue Storage.")
            else:
                self.log.error("Error putting message to the queue.\n" +
                               str(e))