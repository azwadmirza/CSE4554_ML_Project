        def deser(self, obj_msg):

            if 'data' in obj_msg.keys():
                data_msg = json.loads(obj_msg['data'])
                tensor_type = hook_self.types_guard(data_msg['torch_type'])
                data_obj = tensor_type.deser(tensor_type, data_msg)
                # data_obj = hook_self.build_tensor(data_msg, tensor_type)
                data = hook_self.local_worker.handle_register(
                    data_obj, data_msg)

            if 'grad' in obj_msg.keys():
                if obj_msg['grad'] is not None:
                    grad_msg = json.loads(obj_msg['grad'])
                    var_type = hook_self.types_guard(grad_msg['torch_type'])
                    grad_obj = hook_self._build_var(grad_msg, var_type)
                    grad = hook_self.local_worker.handle_register(grad_obj, grad_msg,
                                                                  force_attach_to_worker=False,
                                                                  temporary=True)

                else:
                    grad = None
            var = self(
                data, volatile=obj_msg['volatile'], requires_grad=obj_msg['requires_grad'])
            # var.grad = grad
            if(grad is not None):
                setattr(var, 'grad', grad)
            else:
                var.grad = None

            # this returns grad because garbage collection seems to do something really strange
            # if grad isn't returned here. It re-initializes the gradient somehow but in a way
            # where it's not registered (which is bad)
            return var