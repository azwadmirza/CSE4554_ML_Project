    def to_representation(self, obj):
        serializer_class = None
        if type(self) is UnifiedJobTemplateSerializer:
            if isinstance(obj, Project):
                serializer_class = ProjectSerializer
            elif isinstance(obj, InventorySource):
                serializer_class = InventorySourceSerializer
            elif isinstance(obj, JobTemplate):
                serializer_class = JobTemplateSerializer
            elif isinstance(obj, SystemJobTemplate):
                serializer_class = SystemJobTemplateSerializer
            elif isinstance(obj, WorkflowJobTemplate):
                serializer_class = WorkflowJobTemplateSerializer
        if serializer_class:
            serializer = serializer_class(instance=obj, context=self.context)
            # preserve links for list view
            if self.parent:
                serializer.parent = self.parent
                serializer.polymorphic_base = self
                # capabilities prefetch is only valid for these models
                if isinstance(obj, (JobTemplate, WorkflowJobTemplate)):
                    serializer.capabilities_prefetch = self._capabilities_prefetch
                else:
                    serializer.capabilities_prefetch = None
            return serializer.to_representation(obj)
        else:
            return super(UnifiedJobTemplateSerializer, self).to_representation(obj)