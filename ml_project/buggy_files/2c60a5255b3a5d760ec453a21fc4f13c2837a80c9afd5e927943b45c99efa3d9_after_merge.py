    def create_target_images(self, img, input_path):
        gallery_name = os.path.dirname(img)
        output_gallery = os.path.dirname(
            os.path.join(
                self.kw["output_folder"],
                self.site.path("gallery_global", gallery_name)))
        # Do thumbnails and copy originals
        # img is "galleries/name/image_name.jpg"
        # img_name is "image_name.jpg"
        # fname, ext are "image_name", ".jpg"
        # thumb_path is
        # "output/GALLERY_PATH/name/image_name.thumbnail.jpg"
        img_name = os.path.basename(img)
        fname, ext = os.path.splitext(img_name)
        thumb_path = os.path.join(
            output_gallery,
            ".thumbnail".join([fname, ext]))
        # thumb_path is "output/GALLERY_PATH/name/image_name.jpg"
        orig_dest_path = os.path.join(output_gallery, img_name)
        yield utils.apply_filters({
            'basename': self.name,
            'name': thumb_path,
            'file_dep': [img],
            'targets': [thumb_path],
            'actions': [
                (self.resize_image,
                    (img, thumb_path, self.kw['thumbnail_size']))
            ],
            'clean': True,
            'uptodate': [utils.config_changed({
                1: self.kw['thumbnail_size']
            }, 'nikola.plugins.task.galleries:resize_thumb')],
        }, self.kw['filters'])

        yield utils.apply_filters({
            'basename': self.name,
            'name': orig_dest_path,
            'file_dep': [img],
            'targets': [orig_dest_path],
            'actions': [
                (self.resize_image,
                    (img, orig_dest_path, self.kw['max_image_size']))
            ],
            'clean': True,
            'uptodate': [utils.config_changed({
                1: self.kw['max_image_size']
            }, 'nikola.plugins.task.galleries:resize_max')],
        }, self.kw['filters'])