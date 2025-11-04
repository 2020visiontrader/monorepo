"""
Health check views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db import connection
import redis


class HealthView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        env = getattr(settings, 'ENVIRONMENT', getattr(settings, 'ENV_NAME', 'ST'))
        db_status = 'ok'
        redis_status = 'ok'
        
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except Exception:
            db_status = 'error'
        
        # Check Redis
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url, socket_connect_timeout=1)
            r.ping()
        except Exception:
            redis_status = 'error'
        
        return Response({
            'ok': db_status == 'ok' and redis_status == 'ok',
            'env': env,
            'db': db_status,
            'redis': redis_status,
        })

