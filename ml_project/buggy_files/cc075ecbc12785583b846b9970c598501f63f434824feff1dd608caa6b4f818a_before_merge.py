    def get_return_url(self, request, imageattachment):
        return imageattachment.obj.get_absolute_url()