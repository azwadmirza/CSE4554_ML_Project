        def memory_maps(self):
            """Return process's mapped memory regions as a list of named tuples.
            Fields are explained in 'man proc'; here is an updated (Apr 2012)
            version: http://goo.gl/fmebo
            """
            with open_text("%s/%s/smaps" % (self._procfs_path, self.pid),
                           buffering=BIGGER_FILE_BUFFERING) as f:
                first_line = f.readline()
                current_block = [first_line]

                def get_blocks():
                    data = {}
                    for line in f:
                        fields = line.split(None, 5)
                        if not fields[0].endswith(':'):
                            # new block section
                            yield (current_block.pop(), data)
                            current_block.append(line)
                        else:
                            try:
                                data[fields[0]] = int(fields[1]) * 1024
                            except ValueError:
                                if fields[0].startswith('VmFlags:'):
                                    # see issue #369
                                    continue
                                else:
                                    raise ValueError("don't know how to inte"
                                                     "rpret line %r" % line)
                    yield (current_block.pop(), data)

                ls = []
                if first_line:  # smaps file can be empty
                    for header, data in get_blocks():
                        hfields = header.split(None, 5)
                        try:
                            addr, perms, offset, dev, inode, path = hfields
                        except ValueError:
                            addr, perms, offset, dev, inode, path = \
                                hfields + ['']
                        if not path:
                            path = '[anon]'
                        else:
                            path = path.strip()
                            if (path.endswith(' (deleted)') and not
                                    path_exists_strict(path)):
                                path = path[:-10]
                        ls.append((
                            addr, perms, path,
                            data['Rss:'],
                            data.get('Size:', 0),
                            data.get('Pss:', 0),
                            data.get('Shared_Clean:', 0),
                            data.get('Shared_Dirty:', 0),
                            data.get('Private_Clean:', 0),
                            data.get('Private_Dirty:', 0),
                            data.get('Referenced:', 0),
                            data.get('Anonymous:', 0),
                            data.get('Swap:', 0)
                        ))
            return ls