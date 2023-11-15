    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        If a request path contains biz_cc_id parameter, check if current
        user has perm view_business or return http 403.
        """
        if getattr(view_func, 'login_exempt', False):
            return None
        biz_cc_id = view_kwargs.get('biz_cc_id') or self._get_biz_cc_id_in_rest_request(request)
        if biz_cc_id and str(biz_cc_id) != '0':
            try:
                business = prepare_business(request, cc_id=biz_cc_id)
            except exceptions.Unauthorized:
                # permission denied for target business (irregular request)
                return HttpResponse(status=401)
            except exceptions.Forbidden:
                # target business does not exist (irregular request)
                return HttpResponseForbidden()
            except exceptions.APIError as e:
                ctx = {
                    'system': e.system,
                    'api': e.api,
                    'message': e.message,
                }
                logger.error(json.dumps(ctx))
                return HttpResponse(status=503, content=json.dumps(ctx))

            # set time_zone of business
            if business.time_zone:
                request.session['blueking_timezone'] = business.time_zone

            try:
                if not request.user.has_perm('view_business', business):
                    raise exceptions.Unauthorized(
                        'user[{username}] has no perm view_business of business[{biz}]'.format(
                            username=request.user.username, biz=business.cc_id
                        )
                    )
            except Exception as e:
                logger.exception('user[username={username},type={user_type}] has_perm raise error[{error}]'.format(
                    username=request.user.username,
                    user_type=type(request.user),
                    error=e)
                )
                return HttpResponseForbidden(e.message)