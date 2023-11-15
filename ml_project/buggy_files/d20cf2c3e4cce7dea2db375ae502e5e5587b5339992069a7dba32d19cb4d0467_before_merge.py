    def setup_events(self):
        ## hack - what we want to do is execute the update callback once
        ## and only if some properties in the graph have changed
        ## so we set should_update to be True in setup_events, and
        ## set it to be false as soon as the callback is done
        if not self.name:
            return
        for k in self.__dict__.keys():
            if k.startswith('_func'):
                self.__dict__.pop(k)
        counter = 0
        if not self.update_registry.get(self.name):
            name = '_func%d'  % counter
            func = self.create_registry[self.name]
            setattr(self, name, self.callback(func))
            for widget_name in self.widget_list:
                obj = self.objects.get(widget_name)
                if obj:
                    for attr in obj.class_properties():
                        obj.on_change(attr, self, name)
            return
        for selectors, func in self.update_registry[self.name]:
            #hack because we lookup callbacks by func name
            name = '_func%d'  % counter
            counter += 1
            setattr(self, name, self.callback(func))
            for selector in selectors:
                if isinstance(selector, string_types):
                    self.widget_dict[selector].on_change('value', self, name)
                    continue
                elif isinstance(selector, tuple):
                    selector, attrs = selector
                else:
                    attrs = None
                for obj in self.select(selector):
                    if obj == self:
                        continue
                    if attrs:
                        toiter = attrs
                    else:
                        toiter = obj.class_properties()
                    for attr in toiter:
                        obj.on_change(attr, self, name)
        self.set_debounce()