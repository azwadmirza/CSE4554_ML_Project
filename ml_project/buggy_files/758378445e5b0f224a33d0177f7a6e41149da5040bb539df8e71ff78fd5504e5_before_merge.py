    def __str__(self):
        rows = []

        try:
            if self._filename:
                rows.append(('path', self._filename))

            if self._version == 102 and type(self._reader) == _BagReader102_Unindexed:
                rows.append(('version', '1.2 (unindexed)'))
            else:
                rows.append(('version', '%d.%d' % (int(self._version / 100), self._version % 100)))

            if not self._connection_indexes and not self._chunks:
                rows.append(('size', _human_readable_size(self.size)))
            else:
                if self._chunks:
                    start_stamp = self._chunks[ 0].start_time.to_sec()
                    end_stamp   = self._chunks[-1].end_time.to_sec()
                else:
                    start_stamp = min([index[ 0].time.to_sec() for index in self._connection_indexes.values()])
                    end_stamp   = max([index[-1].time.to_sec() for index in self._connection_indexes.values()])
    
                # Show duration
                duration = end_stamp - start_stamp
                dur_secs = duration % 60
                dur_mins = int(duration / 60)
                dur_hrs  = int(dur_mins / 60)
                if dur_hrs > 0:
                    dur_mins = dur_mins % 60
                    duration_str = '%dhr %d:%02ds (%ds)' % (dur_hrs, dur_mins, dur_secs, duration)
                elif dur_mins > 0:
                    duration_str = '%d:%02ds (%ds)' % (dur_mins, dur_secs, duration)
                else:
                    duration_str = '%.1fs' % duration   

                rows.append(('duration', duration_str))
        
                # Show start and end times
                rows.append(('start', '%s (%.2f)' % (_time_to_str(start_stamp), start_stamp)))
                rows.append(('end',   '%s (%.2f)' % (_time_to_str(end_stamp),   end_stamp)))
    
                rows.append(('size', _human_readable_size(self.size)))

                if self._chunks:
                    num_messages = 0
                    for c in self._chunks:
                        for counts in c.connection_counts.values():
                            num_messages += counts
                else:
                    num_messages = sum([len(index) for index in self._connection_indexes.values()])
                rows.append(('messages', str(num_messages)))

                # Show compression information
                if len(self._chunk_headers) == 0:
                    rows.append(('compression', 'none'))
                else:
                    compression_counts       = {}
                    compression_uncompressed = {}
                    compression_compressed   = {}
                    for chunk_header in self._chunk_headers.values():
                        if chunk_header.compression not in compression_counts:
                            compression_counts[chunk_header.compression] = 1
                            compression_uncompressed[chunk_header.compression] = chunk_header.uncompressed_size
                            compression_compressed[chunk_header.compression] = chunk_header.compressed_size
                        else:
                            compression_counts[chunk_header.compression] += 1
                            compression_uncompressed[chunk_header.compression] += chunk_header.uncompressed_size
                            compression_compressed[chunk_header.compression] += chunk_header.compressed_size
    
                    chunk_count = len(self._chunk_headers)
    
                    compressions = []
                    for count, compression in reversed(sorted([(v, k) for k, v in compression_counts.items()])):
                        if compression != Compression.NONE:
                            fraction = (100.0 * compression_compressed[compression]) / compression_uncompressed[compression]
                            compressions.append('%s [%d/%d chunks; %.2f%%]' % (compression, count, chunk_count, fraction))
                        else:
                            compressions.append('%s [%d/%d chunks]' % (compression, count, chunk_count))
                    rows.append(('compression', ', '.join(compressions)))
    
                    all_uncompressed = (sum([count for c, count in compression_counts.items() if c != Compression.NONE]) == 0)
                    if not all_uncompressed:    
                        total_uncompressed_size = sum((h.uncompressed_size for h in self._chunk_headers.values()))
                        total_compressed_size   = sum((h.compressed_size   for h in self._chunk_headers.values()))
                        
                        total_uncompressed_size_str = _human_readable_size(total_uncompressed_size)
                        total_compressed_size_str   = _human_readable_size(total_compressed_size)
                        total_size_str_length = max([len(total_uncompressed_size_str), len(total_compressed_size_str)])

                        if duration > 0:
                            uncompressed_rate_str = _human_readable_size(total_uncompressed_size / duration)
                            compressed_rate_str   = _human_readable_size(total_compressed_size / duration)
                            rate_str_length = max([len(uncompressed_rate_str), len(compressed_rate_str)])

                            rows.append(('uncompressed', '%*s @ %*s/s' %
                                         (total_size_str_length, total_uncompressed_size_str, rate_str_length, uncompressed_rate_str)))
                            rows.append(('compressed',   '%*s @ %*s/s (%.2f%%)' %
                                         (total_size_str_length, total_compressed_size_str,   rate_str_length, compressed_rate_str, (100.0 * total_compressed_size) / total_uncompressed_size)))
                        else:
                            rows.append(('uncompressed', '%*s' % (total_size_str_length, total_uncompressed_size_str)))
                            rows.append(('compressed',   '%*s' % (total_size_str_length, total_compressed_size_str)))

                datatypes = set()
                datatype_infos = []
                for connection in self._connections.values():
                    if connection.datatype in datatypes:
                        continue
                    datatype_infos.append((connection.datatype, connection.md5sum, connection.msg_def))
                    datatypes.add(connection.datatype)
                    
                topics = sorted(set([c.topic for c in self._get_connections()]))
                topic_datatypes    = {}
                topic_conn_counts  = {}
                topic_msg_counts   = {}
                topic_freqs_median = {}
                for topic in topics:
                    connections = list(self._get_connections(topic))

                    topic_datatypes[topic] = connections[0].datatype
                    topic_conn_counts[topic] = len(connections)

                    msg_count = 0
                    for connection in connections:
                        for chunk in self._chunks:
                            msg_count += chunk.connection_counts.get(connection.id, 0)
                    topic_msg_counts[topic] = msg_count

                    if self._connection_indexes_read:
                        stamps = [entry.time.to_sec() for entry in self._get_entries(connections)]
                        if len(stamps) > 1:
                            periods = [s1 - s0 for s1, s0 in zip(stamps[1:], stamps[:-1])]
                            med_period = _median(periods)
                            if med_period > 0.0:
                                topic_freqs_median[topic] = 1.0 / med_period

                topics = sorted(topic_datatypes.keys())
                max_topic_len       = max([len(topic) for topic in topics])
                max_datatype_len    = max([len(datatype) for datatype in datatypes])
                max_msg_count_len   = max([len('%d' % msg_count) for msg_count in topic_msg_counts.values()])
                max_freq_median_len = max([len(_human_readable_frequency(freq)) for freq in topic_freqs_median.values()]) if len(topic_freqs_median) > 0 else 0

                # Show datatypes       
                for i, (datatype, md5sum, msg_def) in enumerate(sorted(datatype_infos)):
                    s = '%-*s [%s]' % (max_datatype_len, datatype, md5sum)
                    if i == 0:
                        rows.append(('types', s))
                    else:
                        rows.append(('', s))
                    
                # Show topics
                for i, topic in enumerate(topics):
                    topic_msg_count = topic_msg_counts[topic]
                    
                    s = '%-*s   %*d %s' % (max_topic_len, topic, max_msg_count_len, topic_msg_count, 'msgs' if topic_msg_count > 1 else 'msg ')
                    if topic in topic_freqs_median:
                        s += ' @ %*s' % (max_freq_median_len, _human_readable_frequency(topic_freqs_median[topic]))
                    else:
                        s += '   %*s' % (max_freq_median_len, '')

                    s += ' : %-*s' % (max_datatype_len, topic_datatypes[topic])
                    if topic_conn_counts[topic] > 1:
                        s += ' (%d connections)' % topic_conn_counts[topic]
        
                    if i == 0:
                        rows.append(('topics', s))
                    else:
                        rows.append(('', s))
        
        except Exception as ex:
            raise

        first_column_width = max([len(field) for field, _ in rows]) + 1

        s = ''
        for (field, value) in rows:
            if field:
                s += '%-*s %s\n' % (first_column_width, field + ':', value)
            else:
                s += '%-*s %s\n' % (first_column_width, '', value)

        return s.rstrip()