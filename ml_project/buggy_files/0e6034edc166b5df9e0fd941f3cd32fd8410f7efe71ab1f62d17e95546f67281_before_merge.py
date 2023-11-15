    def on_message_received(self, msg):
        row = ','.join([msg.timestamp,
                        msg.arbitration_id,
                        msg.flags,
                        msg.dlc,
                        msg.data])
        self.csv_file.write(row + '\n')