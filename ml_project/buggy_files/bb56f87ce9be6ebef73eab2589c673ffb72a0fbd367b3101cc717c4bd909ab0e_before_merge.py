    def draw(self, renderer, *args, **kwargs):
        magnification = renderer.get_image_magnification()
        shape = [0, 0]
        for image in self.__images:
            if image.mode == MODE_HIDE:
                continue
            for i in range(2):
                shape[i] = max(shape[i], image.pixel_data.shape[i])
        if any([x == 0 for x in shape]):
            return
        border = self.get_border_count()

        vl = self.axes.viewLim
        view_xmin = int(max(0, min(vl.x0, vl.x1) - self.filterrad))
        view_ymin = int(max(0, min(vl.y0, vl.y1) - self.filterrad))
        view_xmax = int(min(shape[1], max(vl.x0, vl.x1) + self.filterrad))
        view_ymax = int(min(shape[0], max(vl.y0, vl.y1) + self.filterrad))
        flip_ud = vl.y0 > vl.y1
        flip_lr = vl.x0 > vl.x1
        if shape[1] <= view_xmin or shape[1] <= -view_xmin or view_xmax <= 0:
            return
        if shape[0] <= view_ymin or shape[0] <= -view_ymin or view_ymax <= 0:
            return

        # First 3 color indices are intensities
        # Last is the alpha

        target = numpy.zeros(
            (view_ymax - view_ymin, view_xmax - view_xmin, 4), numpy.float32
        )

        def get_tile_and_target(pixel_data):
            """Return the visible tile of the image and a view of the target"""
            xmin = max(0, view_xmin)
            ymin = max(0, view_ymin)
            xmax = min(view_xmax, pixel_data.shape[1])
            ymax = min(view_ymax, pixel_data.shape[0])
            if pixel_data.ndim == 3:
                pixel_data = pixel_data[ymin:ymax, xmin:xmax, :]
            else:
                pixel_data = pixel_data[ymin:ymax, xmin:xmax]
            target_view = target[: (ymax - view_ymin), : (xmax - view_xmin), :]
            return pixel_data, target_view

        max_color_in = numpy.zeros(3)
        for image in self.__images:
            assert isinstance(image, ImageData)
            if image.mode == MODE_HIDE:
                continue
            if image.pixel_data.shape[1] <= abs(view_xmin) or image.pixel_data.shape[
                0
            ] <= abs(view_ymin):
                continue
            pixel_data, target_view = get_tile_and_target(image.pixel_data)
            tv_alpha = target_view[:, :, 3]
            tv_image = target_view[:, :, :3]
            if image.normalization in (NORMALIZE_LINEAR, NORMALIZE_LOG):
                pd_max = numpy.max(pixel_data)
                pd_min = numpy.min(pixel_data)
                if pd_min == pd_max:
                    pixel_data = numpy.zeros(pixel_data.shape, numpy.float32)
                else:
                    pixel_data = (pixel_data - pd_min) / (pd_max - pd_min)
            else:
                pixel_data = pixel_data.copy()
                pixel_data[pixel_data < image.vmin] = image.vmin
                pixel_data[pixel_data > image.vmax] = image.vmax
            if image.normalization == NORMALIZE_LOG:
                log_eps = numpy.log(1.0 / 256)
                log_one_plus_eps = numpy.log(257.0 / 256)
                pixel_data = (numpy.log(pixel_data + 1.0 / 256) - log_eps) / (
                    log_one_plus_eps - log_eps
                )
            if image.mode == MODE_COLORIZE or image.mode == MODE_GRAYSCALE:
                pixel_data = pixel_data[:, :, numpy.newaxis] * image.color3
            elif image.mode == MODE_COLORMAP:
                sm = matplotlib.cm.ScalarMappable(cmap=image.colormap)
                if image.normalization == NORMALIZE_RAW:
                    sm.set_clim((image.vmin, image.vmax))
                pixel_data = sm.to_rgba(pixel_data)[:, :, :3]
            max_color_in = numpy.maximum(
                max_color_in,
                numpy.max(
                    pixel_data.reshape(
                        pixel_data.shape[0] * pixel_data.shape[1], pixel_data.shape[2]
                    ),
                    0,
                ),
            )
            imalpha = image.alpha
            tv_image[:] = (
                tv_image * tv_alpha[:, :, numpy.newaxis] * (1 - imalpha)
                + pixel_data * imalpha
            )
            tv_alpha[:] = tv_alpha + imalpha - tv_alpha * imalpha
            tv_image[tv_alpha != 0, :] /= tv_alpha[tv_alpha != 0][:, numpy.newaxis]

        #
        # Normalize the image intensity
        #
        max_color_out = numpy.max(
            target[:, :, :3].reshape(target.shape[0] * target.shape[1], 3), 0
        )
        color_mask = (max_color_in != 0) & (max_color_out != 0)
        if numpy.any(color_mask):
            multiplier = numpy.min(max_color_in[color_mask] / max_color_out[color_mask])
        else:
            multiplier = 1
        target[:, :, :3] *= multiplier

        for om in list(self.__objects) + list(self.__masks):
            assert isinstance(om, OutlinesMixin)
            if om.mode in (MODE_LINES, MODE_HIDE):
                continue
            if om.mode == MODE_OUTLINES:
                oshape = om.outlines.shape
                if oshape[1] <= abs(view_xmin) or oshape[0] <= abs(view_ymin):
                    continue
                mask, target_view = get_tile_and_target(om.outlines)
                oalpha = mask.astype(float) * om.alpha
                ocolor = om.color3
            elif isinstance(om, ObjectsData) and om.mode == MODE_OVERLAY:
                oshape = om.outlines.shape
                if oshape[1] <= abs(view_xmin) or oshape[0] <= abs(view_ymin):
                    continue
                ocolor, target_view = get_tile_and_target(om.overlay[:, :, :3])
                mask, _ = get_tile_and_target(om.mask)
            elif isinstance(om, MaskData) and om.mode in (MODE_OVERLAY, MODE_INVERTED):
                mask = om.mask
                if mask.shape[1] <= abs(view_xmin) or mask.shape[0] <= abs(view_ymin):
                    continue
                mask, target_view = get_tile_and_target(mask)
                if om.mode == MODE_INVERTED:
                    mask = ~mask
                ocolor = mask[:, :, numpy.newaxis] * om.color3
            else:
                continue
            tv_alpha = target_view[:, :, 3]
            tv_image = target_view[:, :, :3]
            tv_alpha3 = tv_alpha[:, :, numpy.newaxis]
            oalpha = mask.astype(float) * om.alpha
            oalpha3 = oalpha[:, :, numpy.newaxis]
            tv_image[:] = tv_image * tv_alpha3 * (1 - oalpha3) + ocolor * oalpha3
            tv_alpha[:] = tv_alpha + oalpha - tv_alpha * oalpha
            tv_image[tv_alpha != 0, :] /= tv_alpha[tv_alpha != 0][:, numpy.newaxis]

        target = target[:, :, :3]

        numpy.clip(target, 0, 1, target)

        if flip_lr:
            target = numpy.fliplr(target)

        if self.axes.viewLim.height < 0:
            target = numpy.flipud(target)

        # im = matplotlib.image.fromarray(target[:, :, :3], 0)
        # im.is_grayscale = False
        # im.set_interpolation(self.mp_interpolation)
        fc = matplotlib.rcParams["axes.facecolor"]
        bg = matplotlib.colors.colorConverter.to_rgba(fc, 0)
        # im.set_bg(*bg)

        # image input dimensions
        # im.reset_matrix()

        # the viewport translation in the X direction
        tx = view_xmin - min(vl.x0, vl.x1) - 0.5

        #
        # the viewport translation in the Y direction
        # which is from the bottom of the screen
        #
        if self.axes.viewLim.height < 0:
            # ty = (view_ymin - self.axes.viewLim.y1) - .5
            ty = self.axes.viewLim.y0 - view_ymax + 0.5
        else:
            ty = view_ymin - self.axes.viewLim.y0 - 0.5

        # im.apply_translation(tx, ty)

        l, b, r, t = self.axes.bbox.extents

        if b > t:
            t, b = b, t

        width_display = (r - l + 1) * magnification
        height_display = (t - b + 1) * magnification

        # resize viewport to display
        sx = width_display / self.axes.viewLim.width
        sy = abs(height_display / self.axes.viewLim.height)

        # im.apply_scaling(sx, sy)
        # im.resize(width_display, height_display, norm=1, radius=self.filterrad)

        bounding_box = self.axes.bbox.frozen()

        graphics_context = renderer.new_gc()

        graphics_context.set_clip_rectangle(bounding_box)

        image = numpy.zeros((target.shape[0], target.shape[1], 4), numpy.uint8)

        image[:, :, 3] = 255

        image[:, :, :3] = skimage.exposure.rescale_intensity(
            target, out_range=numpy.uint8
        )

        image = skimage.transform.rescale(image, (sx, sy, 1))

        image = skimage.img_as_ubyte(image)

        renderer.draw_image(graphics_context, l, b, image)

        for om in list(self.__objects) + list(self.__masks):
            assert isinstance(om, OutlinesMixin)
            if om.mode == MODE_LINES:
                om.points.axes = self.axes
                om.points.set_transform(self.axes.transData)
                om.points.set_clip_path(self.axes.patch)
                om.points.draw(renderer)