    def get_return_url(self, request, imageattachment):
        return imageattachment.parent.get_absolute_url()