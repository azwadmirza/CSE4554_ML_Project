    def do_render(self, cr, widget, background_area, cell_area, flags):

        vw_tags = self.__count_viewable_tags()
        count = 0

        # Select source
        if self.tag_list is not None:
            tags = self.tag_list
        elif self.tag is not None:
            tags = [self.tag]
        else:
            return

        if self.config.get('dark_mode'):
            symbolic_color = Gdk.RGBA(0.9, 0.9, 0.9, 1)
        else:
            symbolic_color = Gdk.RGBA(0, 0, 0, 1)

        # Drawing context
        gdkcontext = cr
        gdkcontext.set_antialias(cairo.ANTIALIAS_NONE)

        # Coordinates of the origin point
        x_align = self.get_property("xalign")
        y_align = self.get_property("yalign")
        padding = self.PADDING
        orig_x = cell_area.x + int((cell_area.width - 16 * vw_tags -
                                    padding * 2 * (vw_tags - 1)) * x_align)
        orig_y = cell_area.y + int((cell_area.height - 16) * y_align)

        # We draw the icons & squares
        for my_tag in tags:

            my_tag_icon = my_tag.get_attribute("icon")
            my_tag_color = my_tag.get_attribute("color")

            rect_x = orig_x + self.PADDING * 2 * count + 16 * count
            rect_y = orig_y


            if my_tag_icon:
                if my_tag_icon in self.SYMBOLIC_ICONS:
                    icon_theme = Gtk.IconTheme.get_default()
                    info = icon_theme.lookup_icon(my_tag_icon, 16, 0)
                    load = info.load_symbolic(symbolic_color)
                    pixbuf = load[0]

                    Gdk.cairo_set_source_pixbuf(gdkcontext, pixbuf,
                                                rect_x, rect_y)
                    gdkcontext.paint()
                    count +=  1

                else:
                    layout = PangoCairo.create_layout(cr)
                    layout.set_markup(my_tag_icon, -1)
                    cr.move_to(rect_x - 2, rect_y - 1)
                    PangoCairo.show_layout(cr, layout)
                    count += 1

            elif my_tag_color:

                # Draw rounded rectangle
                my_color = Gdk.RGBA()
                my_color.parse(my_tag_color)
                Gdk.cairo_set_source_rgba(gdkcontext, my_color)

                self.__roundedrec(gdkcontext, rect_x, rect_y, 16, 16, 8)
                gdkcontext.fill()
                count += 1

                # Outer line
                Gdk.cairo_set_source_rgba(gdkcontext, Gdk.RGBA(0, 0, 0, 0.20))
                gdkcontext.set_line_width(1.0)
                self.__roundedrec(gdkcontext, rect_x, rect_y, 16, 16, 8)
                gdkcontext.stroke()

        if self.tag and my_tag:

            my_tag_icon = my_tag.get_attribute("icon")
            my_tag_color = my_tag.get_attribute("color")

            if not my_tag_icon and not my_tag_color:
                # Draw rounded rectangle
                Gdk.cairo_set_source_rgba(gdkcontext,
                                          Gdk.RGBA(0.95, 0.95, 0.95, 1))
                self.__roundedrec(gdkcontext, rect_x, rect_y, 16, 16, 8)
                gdkcontext.fill()

                # Outer line
                Gdk.cairo_set_source_rgba(gdkcontext, Gdk.RGBA(0, 0, 0, 0.20))
                gdkcontext.set_line_width(1.0)
                self.__roundedrec(gdkcontext, rect_x, rect_y, 16, 16, 8)
                gdkcontext.stroke()