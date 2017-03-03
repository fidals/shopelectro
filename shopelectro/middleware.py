from django_user_agents.middleware import UserAgentMiddleware
from django.utils.deprecation import MiddlewareMixin


class PatchedUserAgentMiddleware(MiddlewareMixin, UserAgentMiddleware):
    """Patch django_user_agent middleware."""
