    def get_arns(self, resources):
        arns = []

        m = self.get_model()
        arn_key = getattr(m, 'arn', None)
        if arn_key is False:
            raise ValueError("%s do not have arns" % self.type)

        id_key = m.id

        for r in resources:
            _id = r[id_key]
            if arn_key:
                arns.append(r[arn_key])
            elif 'arn' in _id[:3]:
                arns.append(_id)
            else:
                arns.append(self.generate_arn(_id))
        return arns