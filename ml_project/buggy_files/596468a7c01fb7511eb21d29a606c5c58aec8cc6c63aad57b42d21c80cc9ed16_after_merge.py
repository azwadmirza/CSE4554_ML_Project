    def finishBuildAction(self, action_id, failure):
        """
        """
        action = self.session.query(BuildAction).get(action_id)
        if action is None:
            # TODO: if file is not needed update reportsToBuildActions.
            return False

        failure = failure.decode('unicode_escape').encode('ascii', 'ignore')

        action.mark_finished(failure)
        self.session.commit()
        return True