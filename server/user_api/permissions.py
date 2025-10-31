from permissions import HasScope

class HasUserReadScope(HasScope):
    scope = 'users:read'


