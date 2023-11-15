    def run_objects(self, workspace):
        objects_name = self.objects_name.value
        objects = workspace.object_set.get_objects(objects_name)
        filename = self.get_filename(workspace)
        if filename is None:  # failed overwrite check
            return

        labels = [l for l, c in objects.get_labels()]
        if self.get_file_format() == FF_MAT:
            pixels = objects.segmented
            scipy.io.matlab.mio.savemat(filename,{"Image":pixels},format='5')
        
        elif self.gray_or_color == GC_GRAYSCALE:
            if objects.count > 255:
                pixel_type = ome.PT_UINT16
            else:
                pixel_type = ome.PT_UINT8
            for i, l in enumerate(labels):
                self.do_save_image(
                    workspace, filename, l, pixel_type, t=i, size_t=len(labels))
        
        else:
            if self.colormap == cps.DEFAULT:
                colormap = cpp.get_default_colormap()
            else:
                colormap = self.colormap.value
            cm = matplotlib.cm.get_cmap(colormap)
                
            cpixels = np.zeros((labels[0].shape[0], labels[0].shape[1], 3))
            counts = np.zeros(labels[0].shape, int)
            mapper = matplotlib.cm.ScalarMappable(cmap=cm)
            for pixels in labels:
                cpixels[pixels != 0, :] += \
                    mapper.to_rgba(distance_color_labels(pixels), 
                                   bytes=True)[pixels != 0, :3]
                counts[pixels != 0] += 1
            counts[counts == 0] = 1
            cpixels = cpixels / counts[:, :, np.newaxis]
            self.do_save_image(workspace, filename, cpixels, ome.PT_UINT8)
        self.save_filename_measurements(workspace)
        if self.show_window:
            workspace.display_data.wrote_image = True