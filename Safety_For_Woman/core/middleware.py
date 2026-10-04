class SecurityHeadersMiddleware:
    """
    Adds hardening HTTP headers to all responses without relying on client-side JS.
    Ensures safe content-type handling, referrer isolation, and enables browser
    sensor permissions (geolocation, mic for speech 'help' trigger, accelerometer for fall detection).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["Referrer-Policy"] = "same-origin"
        response["Permissions-Policy"] = (
            "geolocation=(self), microphone=(self), accelerometer=(self), gyroscope=(self)"
        )
        return response
