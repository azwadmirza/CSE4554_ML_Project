    async def update_last_activity(self):
        """Update User.last_activity timestamps from the proxy"""
        routes = await self.proxy.get_all_routes()
        users_count = 0
        active_users_count = 0
        now = datetime.utcnow()
        for prefix, route in routes.items():
            route_data = route['data']
            if 'user' not in route_data:
                # not a user route, ignore it
                continue
            if 'server_name' not in route_data:
                continue
            users_count += 1
            if 'last_activity' not in route_data:
                # no last activity data (possibly proxy other than CHP)
                continue
            user = orm.User.find(self.db, route_data['user'])
            if user is None:
                self.log.warning("Found no user for route: %s", route)
                continue
            spawner = user.orm_spawners.get(route_data['server_name'])
            if spawner is None:
                self.log.warning("Found no spawner for route: %s", route)
                continue
            dt = parse_date(route_data['last_activity'])
            if dt.tzinfo:
                # strip timezone info to naïve UTC datetime
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

            if user.last_activity:
                user.last_activity = max(user.last_activity, dt)
            else:
                user.last_activity = dt
            if spawner.last_activity:
                spawner.last_activity = max(spawner.last_activity, dt)
            else:
                spawner.last_activity = dt
            # FIXME: Make this configurable duration. 30 minutes for now!
            if (now - user.last_activity).total_seconds() < 30 * 60:
                active_users_count += 1
        self.statsd.gauge('users.running', users_count)
        self.statsd.gauge('users.active', active_users_count)

        self.db.commit()
        await self.proxy.check_routes(self.users, self._service_map, routes)