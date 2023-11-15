    def persistent_id(self, obj):
        if isinstance(obj, ray.ObjectRef):
            obj_id = obj.binary()
            if obj_id not in self.server.object_refs[self.client_id]:
                # We're passing back a reference, probably inside a reference.
                # Let's hold onto it.
                self.server.object_refs[self.client_id][obj_id] = obj
            return PickleStub(
                type="Object",
                client_id=self.client_id,
                ref_id=obj_id,
                name=None,
                baseline_options=None,
            )
        elif isinstance(obj, ray.actor.ActorHandle):
            actor_id = obj._actor_id.binary()
            if actor_id not in self.server.actor_refs:
                # We're passing back a handle, probably inside a reference.
                self.actor_refs[actor_id] = obj
            if actor_id not in self.actor_owners[self.client_id]:
                self.actor_owners[self.client_id].add(actor_id)
            return PickleStub(
                type="Actor",
                client_id=self.client_id,
                ref_id=obj._actor_id.binary(),
                name=None,
                baseline_options=None,
            )
        return None