    def before_content(self):
        # lastname may not be set if there was an error
        if 'cpp:lastname' in self.env.ref_context:
            lastname = self.env.ref_context['cpp:lastname']
            assert lastname
            if 'cpp:parent' in self.env.ref_context:
                self.env.ref_context['cpp:parent'].append(lastname)
            else:
                self.env.ref_context['cpp:parent'] = [lastname]