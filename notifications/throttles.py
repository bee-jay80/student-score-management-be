from rest_framework.throttling import SimpleRateThrottle


class NotificationListThrottle(SimpleRateThrottle):
    scope = 'notifications'

