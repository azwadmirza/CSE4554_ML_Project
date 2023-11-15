    def label_per_data(self, project):
        label_count = Counter()
        user_count = Counter()
        annotation_class = project.get_annotation_class()
        docs = project.documents.all()
        annotations = annotation_class.objects.filter(document_id__in=docs.all())
        for d in annotations.values('label__text', 'user__username').annotate(Count('label'), Count('user')):
            label_count[d['label__text']] += d['label__count']
            user_count[d['user__username']] += d['user__count']
        return label_count, user_count