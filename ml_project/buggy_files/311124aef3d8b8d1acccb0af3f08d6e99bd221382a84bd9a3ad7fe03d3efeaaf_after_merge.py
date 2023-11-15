    def run(self):

        with Database('jellyfin') as jellyfindb:
            database = jellyfin_db.JellyfinDatabase(jellyfindb.cursor)

            while True:

                try:
                    item_id = self.queue.get(timeout=1)
                except Queue.Empty:
                    break

                try:
                    media = database.get_media_by_id(item_id)
                    if media:
                        self.output[media].put({'Id': item_id, 'Type': media})
                    else:
                        items = database.get_media_by_parent_id(item_id)

                        if not items:
                            LOG.info("Could not find media %s in the jellyfin database.", item_id)
                        else:
                            for item in items:
                                self.output[item[1]].put({'Id': item[0], 'Type': item[1]})
                except Exception as error:
                    LOG.exception(error)

                self.queue.task_done()

                if window('jellyfin_should_stop.bool'):
                    break

        LOG.info("--<[ q:sort/%s ]", id(self))
        self.is_done = True