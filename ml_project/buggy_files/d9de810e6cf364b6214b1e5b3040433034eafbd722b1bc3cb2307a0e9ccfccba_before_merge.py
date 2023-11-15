    def export_widgets(self_or_cls, obj, filename, fmt=None, template=None,
                       json=False, json_path='', **kwargs):
        """
        Render and export object as a widget to a static HTML
        file. Allows supplying a custom template formatting string
        with fields to interpolate 'js', 'css' and the main 'html'
        containing the widget. Also provides options to export widget
        data to a json file in the supplied json_path (defaults to
        current path).
        """
        if fmt not in list(self_or_cls.widgets.keys())+['auto', None]:
            raise ValueError("Renderer.export_widget may only export "
                             "registered widget types.")

        if not isinstance(obj, NdWidget):
            if not isinstance(filename, BytesIO):
                filedir = os.path.dirname(filename)
                current_path = os.getcwd()
                html_path = os.path.abspath(filedir)
                rel_path = os.path.relpath(html_path, current_path)
                save_path = os.path.join(rel_path, json_path)
            else:
                save_path = json_path
            kwargs['json_save_path'] = save_path
            kwargs['json_load_path'] = json_path
            widget = self_or_cls.get_widget(obj, fmt, **kwargs)
        else:
            widget = obj

        html = self_or_cls.static_html(widget, fmt, template)
        if isinstance(filename, BytesIO):
            filename.write(html)
            filename.seek(0)
        else:
            with open(filename, 'w') as f:
                f.write(html)