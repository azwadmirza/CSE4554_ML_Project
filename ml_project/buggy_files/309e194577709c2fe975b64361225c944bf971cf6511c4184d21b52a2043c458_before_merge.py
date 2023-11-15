    def _get_yaml_info(self, key=None):
        s = ''

        try:
            if self._filename:
                s += 'path: %s\n' % self._filename

            if self._version == 102 and type(self._reader) == _BagReader102_Unindexed:
                s += 'version: 1.2 (unindexed)\n'
            else:
                s += 'version: %d.%d\n' % (int(self._version / 100), self._version % 100)

            if not self._connection_indexes and not self._chunks:
                s += 'size: %d\n' % self.size
                s += 'indexed: False\n'
            else:
                if self._chunks:
                    start_stamp = self._chunks[ 0].start_time.to_sec()
                    end_stamp   = self._chunks[-1].end_time.to_sec()
                else:
                    start_stamp = min([index[ 0].time.to_sec() for index in self._connection_indexes.values()])
                    end_stamp   = max([index[-1].time.to_sec() for index in self._connection_indexes.values()])
                
                duration = end_stamp - start_stamp
                s += 'duration: %.6f\n' % duration
                s += 'start: %.6f\n' % start_stamp
                s += 'end: %.6f\n' % end_stamp
                s += 'size: %d\n' % self.size
                if self._chunks:
                    num_messages = 0
                    for c in self._chunks:
                        for counts in c.connection_counts.values():
                            num_messages += counts
                else:
                    num_messages = sum([len(index) for index in self._connection_indexes.values()])
                s += 'messages: %d\n' % num_messages
                s += 'indexed: True\n'

                # Show compression information
                if len(self._chunk_headers) == 0:
                    s += 'compression: none\n'
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
    
                    main_compression_count, main_compression = list(reversed(sorted([(v, k) for k, v in compression_counts.items()])))[0]
                    s += 'compression: %s\n' % str(main_compression)
    
                    all_uncompressed = (sum([count for c, count in compression_counts.items() if c != Compression.NONE]) == 0)
                    if not all_uncompressed:    
                        s += 'uncompressed: %d\n' % sum((h.uncompressed_size for h in self._chunk_headers.values()))
                        s += 'compressed: %d\n' % sum((h.compressed_size for h in self._chunk_headers.values()))

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
                s += 'types:\n'
                for i, (datatype, md5sum, msg_def) in enumerate(sorted(datatype_infos)):
                    s += '    - type: %s\n' % datatype
                    s += '      md5: %s\n' % md5sum
                    
                # Show topics
                s += 'topics:\n'
                for i, topic in enumerate(topics):
                    topic_msg_count = topic_msg_counts[topic]
                    
                    s += '    - topic: %s\n' % topic
                    s += '      type: %s\n' % topic_datatypes[topic]
                    s += '      messages: %d\n' % topic_msg_count
                        
                    if topic_conn_counts[topic] > 1:
                        s += '      connections: %d\n' % topic_conn_counts[topic]

                    if topic in topic_freqs_median:
                        s += '      frequency: %.4f\n' % topic_freqs_median[topic]

            if not key:
                return s
            
            class DictObject(object):
                def __init__(self, d):
                    for a, b in d.items():
                        if isinstance(b, (list, tuple)):
                           setattr(self, a, [DictObject(x) if isinstance(x, dict) else x for x in b])
                        else:
                           setattr(self, a, DictObject(b) if isinstance(b, dict) else b)

            obj = DictObject(yaml.load(s))
            try:
                val = eval('obj.' + key)
            except Exception as ex:
                print('Error getting key "%s"' % key, file=sys.stderr)
                return None

            def print_yaml(val, indent=0):
                indent_str = '  ' * indent

                if type(val) is list:
                    s = ''
                    for item in val:
                        s += '%s- %s\n' % (indent_str, print_yaml(item, indent + 1))
                    return s
                elif type(val) is DictObject:
                    s = ''
                    for i, (k, v) in enumerate(val.__dict__.items()):
                        if i != 0:
                            s += indent_str
                        s += '%s: %s' % (k, str(v))
                        if i < len(val.__dict__) - 1:
                            s += '\n'
                    return s
                else:
                    return indent_str + str(val)

            return print_yaml(val)

        except Exception as ex:
            raise