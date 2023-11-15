            def process_csv_row(reader):
                seen = []
                records = []
                for row in reader:
                    cleaned_path = posix_normpath("%s%s%s" % (sp_dir, path_prepender, row[0]))
                    if len(row) == 3:
                        checksum, size = row[1:]
                        if checksum:
                            assert checksum.startswith('sha256='), (self._metadata_dir_full_path,
                                                                    cleaned_path, checksum)
                            checksum = checksum[7:]
                        else:
                            checksum = None
                        size = int(size) if size else None
                    else:
                        checksum = size = None
                    if cleaned_path not in seen and row[0]:
                        seen.append(cleaned_path)
                        records.append((cleaned_path, checksum, size))
                    else:
                        continue
                return tuple(records)