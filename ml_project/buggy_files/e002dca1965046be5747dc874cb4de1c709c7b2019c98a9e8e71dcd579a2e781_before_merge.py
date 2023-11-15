    def __call__(self):
        choice_map = {
            "present": self.init_swarm,
            "join": self.join,
            "absent": self.leave,
            "remove": self.remove,
            "inspect": self.inspect_swarm
        }

        choice_map.get(self.parameters.state)()