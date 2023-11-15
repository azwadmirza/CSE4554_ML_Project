    def sort_args(self):
        return args.make_sort_args(
            validator=args.IndexValidator(
                self.model,
                extra=['candidate_name', 'committee_name', 'candidate_id', 'committee_id'],
            ),
        )