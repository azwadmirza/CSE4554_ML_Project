    def draw(self, renderer):
        magnification = renderer.get_image_magnification()
        shape = [0, 0]
        for image in self.__images:
            if image.mode == MODE_HIDE:
                continue
            for i in range(2):
                shape[i] = max(shape[i], image.pixel_data.shape[i])
        if any([x==0 for x in shape]):
            return
        border = self.get_border_count()
            
        vl = self.axes.viewLim
        view_xmin = int(max(0, min(vl.x0, vl.x1) - self.filterrad))
        view_ymin = int(max(0, min(vl.y0, vl.y1) - self.filterrad))
        view_xmax = int(min(shape[1], max(vl.x0, vl.x1) + self.filterrad))
        view_ymax = int(min(shape[0], max(vl.y0, vl.y1) + self.filterrad))
        flip_ud = vl.y0 > vl.y1
        flip_lr = vl.x0 > vl.x1
        if shape[1] <= view_xmin or shape[1] <= - view_xmin or view_xmax <= 0:
            return
        if shape[0] <= view_ymin or shape[0] <= - view_ymin or view_ymax <= 0:
            return
        
        # First 3 color indices are intensities
        # Second 3 are per-color alpha values
        
        target = np.zeros(
            (view_ymax - view_ymin, view_xmax - view_xmin, 6), np.float32)
        def get_tile_and_target(pixel_data):
            '''Return the visible tile of the image and a view of the target'''
            xmin = max(0, view_xmin)
            ymin = max(0, view_ymin)
            xmax = min(view_xmax, pixel_data.shape[1])
            ymax = min(view_ymax, pixel_data.shape[0])
            pixel_data = pixel_data[ymin:ymax, xmin:xmax]
            if flip_ud:
                pixel_data = np.flipud(pixel_data)
            if flip_lr:
                pixel_data = np.fliplr(pixel_data)
            target_view = target[:(ymax - view_ymin), :(xmax - view_xmin), :]
            return pixel_data, target_view
            
        for image in self.__images:
            assert isinstance(image, ImageData)
            if image.mode == MODE_HIDE:
                continue
            if image.pixel_data.shape[1] <= abs(view_xmin) or \
               image.pixel_data.shape[0] <= abs(view_ymin):
                continue
            pixel_data, target_view = get_tile_and_target(image.pixel_data)
            tv_alpha = target_view[:, :, 3:]
            tv_image = target_view[:, :, :3]
            if image.normalization in (NORMALIZE_LINEAR, NORMALIZE_LOG):
                pd_max = np.max(pixel_data)
                pd_min = np.min(pixel_data)
                if pd_min == pd_max:
                    pixel_data = np.zeros(pixel_data.shape, np.float32)
                else:
                    pixel_data = (pixel_data - pd_min) / (pd_max - pd_min)
            else:
                pixel_data = pixel_data.copy()
                pixel_data[pixel_data < image.vmin] = image.vmin
                pixel_data[pixel_data > image.vmax] = image.vmax
            if image.normalization == NORMALIZE_LOG:
                log_eps = np.log(1.0/256)
                log_one_plus_eps = np.log(257.0 / 256)
                pixel_data = (np.log(pixel_data + 1.0/256) - log_eps) / \
                    (log_one_plus_eps - log_eps)
                
            if image.mode == MODE_COLORIZE or image.mode == MODE_GRAYSCALE:
                # The idea here is that the color is the alpha for each of
                # the three channels.
                if image.mode == MODE_COLORIZE:
                    imalpha = np.array(image.color) * image.alpha / \
                        np.sum(image.color)
                else:
                    imalpha = np.array([image.alpha] * 3)
                pixel_data = pixel_data[:, :, np.newaxis]
                imalpha = imalpha[np.newaxis, np.newaxis, :]    
            else:
                if image.mode == MODE_COLORMAP:
                    sm = matplotlib.cm.ScalarMappable(cmap = image.colormap)
                    if image.normalization == NORMALIZE_RAW:
                        sm.set_clim((image.vmin, image.vmax))
                    pixel_data = sm.to_rgba(pixel_data)[:, :, :3]
                imalpha = image.alpha
            tv_image[:] = \
                tv_image * tv_alpha * (1 - imalpha) + pixel_data * imalpha
            tv_alpha[:] = \
                tv_alpha + imalpha - tv_alpha * imalpha
            tv_image[tv_alpha != 0] /= tv_alpha[tv_alpha != 0]
        
        for om in list(self.__objects) + list(self.__masks):
            assert isinstance(om, OutlinesMixin)
            if om.mode in (MODE_LINES, MODE_HIDE):
                continue
            if om.mode == MODE_OUTLINES:
                oshape = om.outlines.shape
                if oshape[1] <= abs(view_xmin) or \
                   oshape[0] <= abs(view_ymin):
                    continue
                mask, target_view = get_tile_and_target(om.outlines)
                tv_alpha = target_view[:, :, 3:]
                tv_image = target_view[:, :, :3]
                oalpha = (mask.astype(float) * om.alpha)[:, :, np.newaxis]
                ocolor = \
                    np.array(om.color)[np.newaxis, np.newaxis, :]
            elif isinstance(om, ObjectsData) and om.mode == MODE_OVERLAY:
                oshape = om.outlines.shape
                if oshape[1] <= abs(view_xmin) or \
                   oshape[0] <= abs(view_ymin):
                    continue
                ocolor, target_view = get_tile_and_target(
                    om.overlay[:, :, :3])
                oalpha = om.overlay[:, :, 3]* om.alpha
                oalpha = oalpha[:, :, np.newaxis]
            elif isinstance(om, MaskData) and \
                 om.mode in (MODE_OVERLAY, MODE_INVERTED):
                mask = om.mask
                if om.mode == MODE_INVERTED:
                    mask = ~mask
                mask = mask[:, :, np.newaxis]
                color = np.array(om.color, np.float32)[np.newaxis, np.newaxis, :]
                ocolor = mask * color
                oalpha = mask * om.alpha
            else:
                continue
            tv_image[:] = tv_image * tv_alpha * (1 - oalpha) + ocolor * oalpha
            tv_alpha[:] = tv_alpha + oalpha - tv_alpha * oalpha
            tv_image[tv_alpha != 0] /= tv_alpha[tv_alpha != 0]
       
        target = target[:, :, :3]
        np.clip(target, 0, 1, target)
        im = matplotlib.image.fromarray(target[:, :, :3], 0)
        im.is_grayscale = False
        im.set_interpolation(self.mp_interpolation)
        fc = matplotlib.rcParams['axes.facecolor']
        bg = matplotlib.colors.colorConverter.to_rgba(fc, 0)
        im.set_bg( *bg)
        
        # image input dimensions
        im.reset_matrix()

        # the viewport translation in the X direction
        tx = view_xmin - min(vl.x0, vl.x1) - .5
        #
        # the viewport translation in the Y direction
        # which is from the bottom of the screen
        #
        if self.axes.viewLim.height < 0:
            ty = (view_ymin - self.axes.viewLim.y1) + .5
        else:
            ty = view_ymin - self.axes.viewLim.y0 - .5
        im.apply_translation(tx, ty)
        l, b, r, t = self.axes.bbox.extents
        if b > t:
            t, b = b, t
        widthDisplay = (r - l + 1) * magnification
        heightDisplay = (t - b + 1) * magnification

        # resize viewport to display
        sx = widthDisplay / self.axes.viewLim.width
        sy = abs(heightDisplay  / self.axes.viewLim.height)
        im.apply_scaling(sx, sy)
        im.resize(widthDisplay, heightDisplay,
                  norm=1, radius = self.filterrad)
        bbox = self.axes.bbox.frozen()
        
        # Two ways to do this, try by version
        mplib_version = matplotlib.__version__.split(".")
        if mplib_version[0] == '0':
            renderer.draw_image(l, b, im, bbox)
        else:
            gc = renderer.new_gc()
            gc.set_clip_rectangle(bbox)
            renderer.draw_image(gc, l, b, im)
        for om in list(self.__objects) + list(self.__masks):
            assert isinstance(om, OutlinesMixin)
            if om.mode == MODE_LINES:
                om.points.set_axes(self.axes)
                om.points.set_transform(self.axes.transData)
                om.points.set_clip_path(self.axes.patch)
                om.points.draw(renderer)