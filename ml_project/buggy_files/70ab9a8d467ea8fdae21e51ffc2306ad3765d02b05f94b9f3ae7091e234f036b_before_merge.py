    def add_vote(self, translation, request, positive):
        '''
        Adds (or updates) vote for a suggestion.
        '''
        vote, created = Vote.objects.get_or_create(
            suggestion=self,
            user=request.user,
            defaults={'positive': positive}
        )
        if not created or vote.positive != positive:
            vote.positive = positive
            vote.save()

        # Automatic accepting
        required_votes = translation.subproject.suggestion_autoaccept
        if required_votes and self.get_num_votes() >= required_votes:
            self.accept(translation, request)