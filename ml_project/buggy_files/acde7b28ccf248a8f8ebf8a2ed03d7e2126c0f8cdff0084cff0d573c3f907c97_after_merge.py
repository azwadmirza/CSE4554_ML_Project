    def put_if_absent(self, k, v, use_serialize=True):
        return _EggRoll.get_instance().put_if_absent(self, k, v, use_serialize=use_serialize)