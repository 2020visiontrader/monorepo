"""
Custom throttling classes
"""
from rest_framework.throttling import UserRateThrottle


class ContentGenerateThrottle(UserRateThrottle):
    """10 requests per minute for content generation"""
    scope = 'content_generate'


class CompetitorRecrawlThrottle(UserRateThrottle):
    """3 requests per minute for competitor recrawl"""
    scope = 'competitor_recrawl'


class JobLogsThrottle(UserRateThrottle):
    """60 requests per minute for job logs"""
    scope = 'job_logs'

