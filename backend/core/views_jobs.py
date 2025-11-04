"""
Job logs views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from .models import BackgroundJob
from core.permissions import IsAuthenticated, IsEditorOrAbove
from core.throttling import JobLogsThrottle


@api_view(['GET'])
@permission_classes([IsEditorOrAbove])
@throttle_classes([JobLogsThrottle])
def job_logs_view(request, job_id):
    """Get job logs with pagination"""
    try:
        job = BackgroundJob.objects.get(id=job_id)
    except BackgroundJob.DoesNotExist:
        return Response(
            {'detail': 'Job not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check cross-brand access
    if job.brand_id and job.brand_id != getattr(request, 'brand_id', None):
        return Response(
            {'detail': 'Job not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Pagination params - cap at 500, default 200
    offset = int(request.query_params.get('offset', 0))
    limit = min(int(request.query_params.get('limit', 200)), 500)  # Cap at 500
    
    # Get logs from JobLog if exists
    try:
        from .models import JobLog
        from django.db.models import Max
        from datetime import datetime
        
        # Get all logs for grouping by step
        all_logs = JobLog.objects.filter(job=job).order_by('step', 'idx')
        
        # Group by step
        steps_dict = {}
        for log in all_logs:
            if log.step not in steps_dict:
                steps_dict[log.step] = {
                    'name': log.step,
                    'status': 'completed',  # TODO: derive from logs
                    'started_at': log.created_at.isoformat() if log.idx == 0 else None,
                    'finished_at': None,
                    'lines': []
                }
            
            # Get step start/finish times
            step_logs = JobLog.objects.filter(job=job, step=log.step).order_by('idx')
            if step_logs.exists():
                steps_dict[log.step]['started_at'] = step_logs.first().created_at.isoformat()
                steps_dict[log.step]['finished_at'] = step_logs.last().created_at.isoformat()
            
            # Add line (respecting pagination)
            if len(steps_dict[log.step]['lines']) < (offset + limit):
                steps_dict[log.step]['lines'].append({
                    'ts': log.created_at.isoformat(),
                    'level': log.level,
                    'msg': log.message,
                    'idx': log.idx,
                })
        
        # Apply pagination to lines within steps
        steps = []
        for step_name, step_data in steps_dict.items():
            step_lines = step_data['lines']
            paginated_lines = step_lines[offset:offset + limit]
            steps.append({
                'name': step_data['name'],
                'status': step_data['status'],
                'started_at': step_data['started_at'],
                'finished_at': step_data['finished_at'],
                'lines': paginated_lines,
            })
        
        # Calculate next_offset
        total_lines = sum(len(s['lines']) for s in steps_dict.values())
        next_offset = offset + limit if (offset + limit) < total_lines else None
        
        return Response({
            'id': str(job.id),
            'status': job.status.lower(),
            'steps': steps,
            'next_offset': next_offset,
        })
    except (ImportError, AttributeError):
        # Fallback if JobLog doesn't exist
        return Response({
            'id': str(job.id),
            'status': job.status.lower(),
            'steps': [],
            'next_offset': None,
        })
