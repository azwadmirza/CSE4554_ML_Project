    def get_tags_for_dynamic_obj(self, mid=None):
        """
        Return list of tag object details associated with object
        Args:
            mid: Dynamic object for specified object

        Returns: List of tag object details associated with the given object

        """
        tags = []
        if mid is None:
            return tags

        temp_tags_model = self.get_tags_for_object(dobj=mid)

        category_service = self.api_client.tagging.Category

        for tag_obj in temp_tags_model:
            tags.append({
                'id': tag_obj.id,
                'category_name': category_service.get(tag_obj.category_id).name,
                'name': tag_obj.name,
                'description': tag_obj.description,
                'category_id': tag_obj.category_id,
            })

        return tags