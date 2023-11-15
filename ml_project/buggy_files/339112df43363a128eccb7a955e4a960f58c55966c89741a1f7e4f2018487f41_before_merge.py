    def _task_process_alerts(self):
        for hops, ltsession in self.ltsessions.items():
            if ltsession:
                for alert in ltsession.pop_alerts():
                    self.process_alert(alert, hops=hops)

        # We have a separate session for metainfo requests.
        # For this session we are only interested in the metadata_received_alert.
        if self.ltsession_metainfo:
            for alert in self.ltsession_metainfo.pop_alerts():
                if isinstance(alert, lt.metadata_received_alert):
                    self.got_metainfo(str(alert.handle.info_hash()))
                elif alert.__class__.__name__ == "dht_pkt_alert":
                    # We received a raw DHT message - decode it and check whether it is a BEP33 message.
                    decoded = bdecode(alert.pkt_buf)
                    if 'r' in decoded:
                        if 'BFsd' in decoded['r'] and 'BFpe' in decoded['r']:
                            self.dht_health_manager.received_bloomfilters(decoded['r']['id'],
                                                                          bytearray(decoded['r']['BFsd']),
                                                                          bytearray(decoded['r']['BFpe']))