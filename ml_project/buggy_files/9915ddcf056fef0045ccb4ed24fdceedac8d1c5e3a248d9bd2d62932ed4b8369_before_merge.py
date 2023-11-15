    def parse_logs(self, file_type, root, s_name, fn, f, **kw):
        log.debug("Parsing %s/%s", root, fn)
        if not file_type in file_types:
            log.error("Unknown output type '%s'. Error in config?", file_type)
            return False
        log_descr = file_types[file_type]
        if 'not_implemented' in log_descr:
            log.debug("Can't parse '%s' -- implementation missing", file_type)
            return False

        cols = log_descr['cols']
        if isinstance(cols, OrderedDict):
            cols = list(cols.keys())

        kv = {}
        data = {}
        for line_number, line in enumerate(f, start=1):
            line = line.strip().split('\t')
            if line[0][0] == '#':
                # It's a header row
                line[0] = line[0][1:] # remove leading '#'

                if line[0] != cols[0]:
                    # It's not the table header, it must be a key-value row
                    if len(line) == 3 and file_type == "stats":
                        # This is a special case for the 'stats' file type:
                        # The first line _might_ have three columns if processing paired-end reads,
                        # but we don't care about the first line.
                        # The third line is always three columns, which is what we really want.
                        if line[0] == "File":
                            continue
                        kv["Percent filtered"] = float(line[2].strip("%"))
                        kv[line[0]] = line[1]
                    elif len(line) != 2:
                        # Not two items? Wrong!
                        log.error("Expected key value pair in %s/%s:%d but found '%s'",
                                  root, s_name, line_number, repr(line))
                        log.error("Table header should begin with '%s'",
                                  cols[0])
                    else:
                        # save key value pair
                        kv[line[0]] = line[1]
                else:
                    # It should be the table header. Verify:
                    if line != cols:
                        if line != cols + list(log_descr['extracols'].keys()):
                            log.error("Table headers do not match those 'on file'. %s != %s",
                                      repr(line), repr(cols))
                        return False
            else:
                if isinstance(log_descr['cols'], OrderedDict):
                    line = [
                        value_type(value)
                        for value_type, value in zip(log_descr['cols'].values(), line)
                    ]
                else:
                    line = list(map(int, line))
                data[line[0]] = line[1:]

        if s_name in self.mod_data[file_type]:
            log.debug("Duplicate sample name found! Overwriting: %s", s_name)

        self.mod_data[file_type][s_name] = {'data':data, 'kv': kv}
        log.debug("Found %s output for sample %s with %d rows",
                  file_type, s_name, len(data))

        return True