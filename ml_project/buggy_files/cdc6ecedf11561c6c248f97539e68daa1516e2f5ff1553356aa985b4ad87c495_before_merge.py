        def _validate_valid_in():
            if self.valid_in:
                valid_in_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.valid_in)
                valid_in_date = valid_in_date.strftime('%Y%m%d%H%M%SZ')
                if not (valid_in_date >= self.cert.get_notBefore() and valid_in_date <= self.cert.get_notAfter()):
                    self.message.append(
                        'Certificate is not valid in %s seconds from now (%s) - notBefore: %s - notAfter: %s' % (self.valid_in,
                                                                                                                 valid_in_date,
                                                                                                                 self.cert.get_notBefore(),
                                                                                                                 self.cert.get_notAfter())
                    )