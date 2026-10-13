from rest_framework.throttling import SimpleRateThrottle


class OTPRateThrottle(SimpleRateThrottle):
    scope = 'otp'

    def get_cache_key(self, request, view):
        if not self.rate:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

