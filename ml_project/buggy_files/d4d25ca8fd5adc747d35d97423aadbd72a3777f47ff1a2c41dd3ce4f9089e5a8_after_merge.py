    def get_resource_date(self, asg):
        cfg = self.launch_info.get(asg)
        if cfg is None:
            cfg = {}
        ami = self.images.get(cfg.get('ImageId'), {})
        return parse(ami.get(
            self.date_attribute, "2000-01-01T01:01:01.000Z"))