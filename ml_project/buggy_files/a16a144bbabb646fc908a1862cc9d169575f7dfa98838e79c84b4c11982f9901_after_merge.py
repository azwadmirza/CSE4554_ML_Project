        def add_torrents_from_dir(self, torrents_dir, recursive=False):
            # TODO: Optimize this properly!!!!
            torrents_list = []
            errors_list = []

            if recursive:
                def rec_gen():
                    for root, _, filenames in os.walk(torrents_dir):
                        for fn in filenames:
                            yield os.path.join(root, fn)

                filename_generator = rec_gen()
            else:
                filename_generator = os.listdir(torrents_dir)

            # Build list of .torrents to process
            for f in filename_generator:
                filepath = ensure_unicode(
                    os.path.join(ensure_unicode(torrents_dir, 'utf-8'), ensure_unicode(f, 'utf-8')), 'utf-8')
                if os.path.isfile(filepath) and ensure_unicode(f, 'utf-8').endswith(u'.torrent'):
                    torrents_list.append(filepath)

            for chunk in chunks(torrents_list, 100):  # 100 is a reasonable chunk size for commits
                for f in chunk:
                    try:
                        self.add_torrent_to_channel(TorrentDef.load(f))
                    except DuplicateTorrentFileError:
                        pass
                    except:
                        errors_list.append(f)
                orm.commit()  # Kinda optimization to drop excess cache?

            return torrents_list, errors_list