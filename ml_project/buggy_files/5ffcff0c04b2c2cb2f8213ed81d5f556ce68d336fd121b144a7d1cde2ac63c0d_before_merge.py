        def data_xy(mouse_event):
            '''Return the mouse event's x & y converted into data-relative coords'''
            x = mouse_event.xdata
            y = mouse_event.ydata
            return x, y