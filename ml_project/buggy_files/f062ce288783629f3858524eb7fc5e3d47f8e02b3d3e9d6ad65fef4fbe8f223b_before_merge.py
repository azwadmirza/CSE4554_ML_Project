    def on_task_modify(self, task, config):
        # Only scan through accepted entries, as the file must have been downloaded in order to parse anything
        for entry in task.accepted:
            # skip if entry does not have file assigned
            if 'file' not in entry:
                log.trace('%s doesn\'t have a file associated', entry['title'])
                continue
            if not os.path.exists(entry['file']):
                log.debug('File %s does not exist', entry['file'])
                continue
            if os.path.getsize(entry['file']) == 0:
                log.debug('File %s is 0 bytes in size', entry['file'])
                continue
            if not is_torrent_file(entry['file']):
                continue
            log.debug('%s seems to be a torrent', entry['title'])

            # create torrent object from torrent
            try:
                with open(entry['file'], 'rb') as f:
                    # NOTE: this reads entire file into memory, but we're pretty sure it's
                    # a small torrent file since it starts with TORRENT_RE
                    data = f.read()

                if 'content-length' in entry:
                    if len(data) != entry['content-length']:
                        entry.fail('Torrent file length doesn\'t match to the one reported by the server')
                        self.purge(entry)
                        continue

                # construct torrent object
                try:
                    torrent = Torrent(data)
                except SyntaxError as e:
                    entry.fail('%s - broken or invalid torrent file received' % e.args[0])
                    self.purge(entry)
                    continue

                entry['torrent'] = torrent
                entry['torrent_info_hash'] = torrent.info_hash
                # if we do not have good filename (by download plugin)
                # for this entry, try to generate one from torrent content
                if entry.get('filename'):
                    if not entry['filename'].lower().endswith('.torrent'):
                        # filename present but without .torrent extension, add it
                        entry['filename'] += '.torrent'
                else:
                    # generate filename from torrent or fall back to title plus extension
                    entry['filename'] = self.make_filename(torrent, entry)
            except Exception as e:
                log.exception(e)