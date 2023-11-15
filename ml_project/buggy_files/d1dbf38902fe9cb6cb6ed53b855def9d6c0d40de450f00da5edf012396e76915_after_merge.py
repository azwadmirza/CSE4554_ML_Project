    def before_content(self):
        lastname = self.env.ref_context['cpp:lastname']
        assert lastname
        if 'cpp:parent' in self.env.ref_context:
            self.env.ref_context['cpp:parent'].append(lastname)
        else:
            self.env.ref_context['cpp:parent'] = [lastname]