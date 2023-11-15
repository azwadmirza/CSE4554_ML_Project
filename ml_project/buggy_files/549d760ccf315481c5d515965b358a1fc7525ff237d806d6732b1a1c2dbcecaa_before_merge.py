    def _save_group(self, group_id, result):
        self.set(self.get_key_for_group(group_id),
                 self.encode({'result': result.as_tuple()}), states.SUCCESS)
        return result