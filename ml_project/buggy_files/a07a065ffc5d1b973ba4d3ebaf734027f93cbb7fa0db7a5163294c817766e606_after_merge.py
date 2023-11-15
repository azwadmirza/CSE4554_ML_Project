    def paste(self, im, box=None):
        """
        Paste a PIL image into the photo image.  Note that this can
        be very slow if the photo image is displayed.

        :param im: A PIL image. The size must match the target region.  If the
                   mode does not match, the image is converted to the mode of
                   the bitmap image.
        :param box: A 4-tuple defining the left, upper, right, and lower pixel
                    coordinate. See :ref:`coordinate-system`. If None is given
                    instead of a tuple, all of the image is assumed.
        """

        # convert to blittable
        im.load()
        image = im.im
        if image.isblock() and im.mode == self.__mode:
            block = image
        else:
            block = image.new_block(self.__mode, im.size)
            image.convert2(block, image)  # convert directly between buffers

        tk = self.__photo.tk

        try:
            tk.call("PyImagingPhoto", self.__photo, block.id)
        except tkinter.TclError:
            # activate Tkinter hook
            try:
                from . import _imagingtk
                try:
                    if hasattr(tk, 'interp'):
                        # Required for PyPy, which always has CFFI installed
                        from cffi import FFI
                        ffi = FFI()

                        # PyPy is using an FFI CDATA element
                        # (Pdb) self.tk.interp
                        #  <cdata 'Tcl_Interp *' 0x3061b50>
                        _imagingtk.tkinit(
                            int(ffi.cast("uintptr_t", tk.interp)), 1)
                    else:
                        _imagingtk.tkinit(tk.interpaddr(), 1)
                except AttributeError:
                    _imagingtk.tkinit(id(tk), 0)
                tk.call("PyImagingPhoto", self.__photo, block.id)
            except (ImportError, AttributeError, tkinter.TclError):
                raise  # configuration problem; cannot attach to Tkinter