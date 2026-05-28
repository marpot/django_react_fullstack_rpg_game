import traceback
import logging

logger = logging.getLogger("django.request")


class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error("🔥 Unhandled exception", exc_info=exception)
        print("🔥 TRACEBACK:")
        print(traceback.format_exc())
        return None