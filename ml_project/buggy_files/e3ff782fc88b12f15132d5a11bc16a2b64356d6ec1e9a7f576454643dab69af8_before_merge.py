        def fn():
            cellprofiler.utilities.jutil.attach()
            with self.image_dict_lock:
                generation = self.image_dict_generation
                
            for k, v in well.iteritems():
                sd = {}
                with self.image_dict_lock:
                    if self.image_dict_generation > generation:
                        return
                    self.image_dict[k] = sd
                for c, fd in enumerate(v):
                    if PlateData.D_CHANNEL in fd:
                        channel = fd[PlateData.D_CHANNEL]
                    else:
                        channel = str(c+1)
                    img = load_using_bioformats_url(fd[PlateData.D_FILENAME])
                    with self.image_dict_lock:
                        if self.image_dict_generation > generation:
                            return
                        sd[channel] = img
            wx.CallAfter(self.update_figure)
            cellprofiler.utilities.jutil.detach()