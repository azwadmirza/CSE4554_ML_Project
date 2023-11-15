    def format_fee_rate(self, fee_rate):
        return format_fee_satoshis(fee_rate/1000, num_zeros=self.num_zeros) + ' sat/byte'