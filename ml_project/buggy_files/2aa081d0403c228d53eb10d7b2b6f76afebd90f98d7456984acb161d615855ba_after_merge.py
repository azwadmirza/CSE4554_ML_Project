    def take_action(self, parsed_args):
        import os

        self.log.debug('take_action(%s)', parsed_args)

        account = self.app.client_manager.get_account()
        container = parsed_args.container
        objs = self.app.client_manager.storage.object_list(
            account, container)

        for obj in objs['objects']:
            obj_name = obj['name']
            _, stream = self.app.client_manager.storage.object_fetch(
                account, container, obj_name, properties=False)

            if not os.path.exists(os.path.dirname(obj_name)):
                if len(os.path.dirname(obj_name)) > 0:
                    os.makedirs(os.path.dirname(obj_name))
            with open(obj_name, 'wb') as f:
                for chunk in stream:
                    f.write(chunk)