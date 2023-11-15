    def __draw(self, cr):
        """Draws the widget"""
        alloc = self.get_allocation()
        # FIXME - why to use a special variables?
        alloc_w, alloc_h = alloc.width, alloc.height
        # Drawing context
        # cr_ctxt    = Gdk.cairo_create(self.window)
        # gdkcontext = Gdk.CairoContext(cr_ctxt)
        # FIXME
        gdkcontext = cr

        # Draw rectangle
        if self.color is not None:
            my_color = Gdk.RGBA()
            my_color.parse(self.color)
            Gdk.cairo_set_source_rgba(gdkcontext, my_color)
        else:
            Gdk.cairo_set_source_rgba(gdkcontext, Gdk.RGBA(0, 0, 0, 0))
        gdkcontext.rectangle(0, 0, alloc_w, alloc_h)
        gdkcontext.fill()

        # Outer line
        Gdk.cairo_set_source_rgba(gdkcontext, Gdk.RGBA(0, 0, 0, 0.30))
        gdkcontext.set_line_width(2.0)
        gdkcontext.rectangle(0, 0, alloc_w, alloc_h)
        gdkcontext.stroke()

        # If selected draw a symbol
        if(self.selected):
            size = alloc_h * 0.50 - 3
            pos_x = math.floor((alloc_w - size) / 2)
            pos_y = math.floor((alloc_h - size) / 2)
            Gdk.cairo_set_source_rgba(gdkcontext,
                                      Gdk.RGBA(255, 255, 255, 0.80))
            gdkcontext.arc(
                alloc_w / 2, alloc_h / 2, size / 2 + 3, 0, 2 * math.pi)
            gdkcontext.fill()
            gdkcontext.set_line_width(1.0)
            Gdk.cairo_set_source_rgba(gdkcontext, Gdk.RGBA(0, 0, 0, 0.20))
            gdkcontext.arc(
                alloc_w / 2, alloc_h / 2, size / 2 + 3, 0, 2 * math.pi)
            gdkcontext.stroke()
            Gdk.cairo_set_source_rgba(gdkcontext, Gdk.RGBA(0, 0, 0, 0.50))
            gdkcontext.set_line_width(3.0)
            gdkcontext.move_to(pos_x, pos_y + size / 2)
            gdkcontext.line_to(pos_x + size / 2, pos_y + size)
            gdkcontext.line_to(pos_x + size, pos_y)
            gdkcontext.stroke()