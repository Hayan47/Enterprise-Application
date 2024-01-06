from django.utils.deprecation import MiddlewareMixin
import logging 

logger = logging.getLogger(__name__)

class RequestResponseLoggingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        user = request.user
        logger.info('Request: User: %s : %s %s' % (request.user, request.method, request.path))
        

    def process_response(self, request, response):
        user = request.user
        logger.info('Response: User: %s : %s %s %s' % (request.user, request.method, request.path, response.status_code))
        return response