    def save_image(self, workspace):
        if self.show_window:
            workspace.display_data.wrote_image = False
        image = workspace.image_set.get_image(self.image_name.value)
        if self.save_image_or_figure == IF_IMAGE:
            pixels = image.pixel_data
            u16hack = (self.get_bit_depth() == '16' and
                       pixels.dtype.kind in ('u', 'i'))
            if self.file_format != FF_MAT:
                if self.rescale.value:
                    pixels = pixels.copy()
                    # Normalize intensities for each channel
                    if pixels.ndim == 3:
                        # RGB
                        for i in range(3):
                            img_min = np.min(pixels[:,:,i])
                            img_max = np.max(pixels[:,:,i])
                            if img_max > img_min:
                                pixels[:,:,i] = (pixels[:,:,i] - img_min) / (img_max - img_min)
                    else:
                        # Grayscale
                        img_min = np.min(pixels)
                        img_max = np.max(pixels)
                        if img_max > img_min:
                            pixels = (pixels - img_min) / (img_max - img_min)
                elif not u16hack:
                    # Clip at 0 and 1
                    if np.max(pixels) > 1 or np.min(pixels) < 0:
                        sys.stderr.write(
                            "Warning, clipping image %s before output. Some intensities are outside of range 0-1" %
                            self.image_name.value)
                        pixels = pixels.copy()
                        pixels[pixels < 0] = 0
                        pixels[pixels > 1] = 1
                        
                if pixels.ndim == 2 and self.colormap != CM_GRAY:
                    # Convert grayscale image to rgb for writing
                    if self.colormap == cps.DEFAULT:
                        colormap = cpp.get_default_colormap()
                    else:
                        colormap = self.colormap.value
                    cm = matplotlib.cm.get_cmap(colormap)
                    
                    if self.get_bit_depth() == '8':
                        mapper = matplotlib.cm.ScalarMappable(cmap=cm)
                        pixels = mapper.to_rgba(pixels, bytes=True)
                        pixel_type = ome.PT_UINT8
                    else:
                        pixel_type = ome.PT_UINT16
                        pixels *= 255
                elif self.get_bit_depth() == '8':
                    pixels = (pixels*255).astype(np.uint8)
                    pixel_type = ome.PT_UINT8
                else:
                    if not u16hack:
                        pixels = (pixels*65535)
                    pixel_type = ome.PT_UINT16
                
        elif self.save_image_or_figure == IF_MASK:
            pixels = image.mask.astype(np.uint8) * 255
            pixel_type = ome.PT_BIT
            
        elif self.save_image_or_figure == IF_CROPPING:
            pixels = image.crop_mask.astype(np.uint8) * 255
            pixel_type = ome.PT_BIT

        filename = self.get_filename(workspace)
        if filename is None:  # failed overwrite check
            return

        if self.get_file_format() == FF_MAT:
            scipy.io.matlab.mio.savemat(filename,{"Image":pixels},format='5')
        elif self.get_file_format() == FF_BMP:
            save_bmp(filename, pixels)
        else:
            self.do_save_image(workspace, filename, pixels, pixel_type)
        if self.show_window:
            workspace.display_data.wrote_image = True
        if self.when_to_save != WS_LAST_CYCLE:
            self.save_filename_measurements(workspace)