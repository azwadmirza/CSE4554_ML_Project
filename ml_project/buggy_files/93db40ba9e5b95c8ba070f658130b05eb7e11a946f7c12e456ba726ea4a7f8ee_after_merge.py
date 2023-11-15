    def dump(self, instance, instance_type, val):
        if val:
            return text_type(val)
        else:
            val = instance.channel  # call __get__
            return text_type(val)