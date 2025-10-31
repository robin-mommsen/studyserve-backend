from permissions import HasScope

class HasServiceConfigReadScope(HasScope):
    scope = 'service_configs:read'


