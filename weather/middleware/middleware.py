# middleware.py
class CacheRequestBodyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cache the request body if not already cached.
        if not hasattr(request, '_cached_body'):
            try:
                # This reads and caches the body.
                request._cached_body = request.body
            except Exception:
                request._cached_body = b""
        response = self.get_response(request)
        return response
