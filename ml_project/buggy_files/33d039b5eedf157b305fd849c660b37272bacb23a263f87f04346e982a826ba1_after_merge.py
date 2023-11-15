            def __init__(self, center, radius):
                """Draw an ellipse with control points at the ellipse center and
                a given x and y radius"""
                self.center_x, self.center_y = center
                self.radius_x = self.center_x + radius[0] / 2
                self.radius_y = self.center_y + radius[1] / 2
                color = cellprofiler.preferences.get_primary_outline_color()
                color = numpy.hstack((color, [255])).astype(float) / 255.0
                self.ellipse = matplotlib.patches.Ellipse(center, self.width, self.height,
                                                          edgecolor=color,
                                                          facecolor="none")
                self.center_handle = Handle(self.center_x, self.center_y,
                                            self.move_center)
                self.radius_handle = Handle(self.radius_x, self.radius_y,
                                            self.move_radius)