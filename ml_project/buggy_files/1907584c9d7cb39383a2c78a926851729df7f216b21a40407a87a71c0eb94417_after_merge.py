    def _queue_renamed(self,
                       src_path,
                       is_directory,
                       ref_snapshot,
                       new_snapshot):
        """
        Compares information from two directory snapshots (one taken before
        the rename operation and another taken right after) to determine the
        destination path of the file system object renamed, and adds
        appropriate events to the event queue.
        """
        try:
            ref_stat_info = ref_snapshot.stat_info(src_path)
        except KeyError:
            # Probably caught a temporary file/directory that was renamed
            # and deleted. Fires a sequence of created and deleted events
            # for the path.
            if is_directory:
                self.queue_event(DirCreatedEvent(src_path))
                self.queue_event(DirDeletedEvent(src_path))
            else:
                self.queue_event(FileCreatedEvent(src_path))
                self.queue_event(FileDeletedEvent(src_path))
                # We don't process any further and bail out assuming
            # the event represents deletion/creation instead of movement.
            return

        try:
            dest_path = absolute_path(
                new_snapshot.path(ref_stat_info.st_ino))
            if is_directory:
                event = DirMovedEvent(src_path, dest_path)
                # TODO: Do we need to fire moved events for the items
                # inside the directory tree? Does kqueue does this
                # all by itself? Check this and then enable this code
                # only if it doesn't already.
                # A: It doesn't. So I've enabled this block.
                if self.watch.is_recursive:
                    for sub_event in event.sub_moved_events():
                        self.queue_event(sub_event)
                self.queue_event(event)
            else:
                self.queue_event(FileMovedEvent(src_path, dest_path))
        except KeyError:
            # If the new snapshot does not have an inode for the
            # old path, we haven't found the new name. Therefore,
            # we mark it as deleted and remove unregister the path.
            if is_directory:
                self.queue_event(DirDeletedEvent(src_path))
            else:
                self.queue_event(FileDeletedEvent(src_path))