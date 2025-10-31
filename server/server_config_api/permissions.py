from permissions import HasScope

class HasServerConfigReadScope(HasScope):
    scope = 'server_configs:read'
