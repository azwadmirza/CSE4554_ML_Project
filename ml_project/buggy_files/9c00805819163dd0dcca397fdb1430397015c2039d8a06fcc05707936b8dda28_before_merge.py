    def as_story_string(self):
        props = json.dumps({self.key: self.value})
        return "{name}{props}".format(name=self.type_name, props=props)