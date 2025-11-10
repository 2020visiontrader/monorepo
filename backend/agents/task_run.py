"""
Task execution logging for background agents.

Provides functions to record the start and end of agent task executions
for monitoring, debugging, and operational visibility.
"""

from django.utils import timezone
from core.models import TaskRun


def record_task_start(agent_name: str, payload: dict) -> TaskRun:
    """
    Record the start of an agent task execution.

    Args:
        agent_name: Name of the agent (e.g., 'brands_agent')
        payload: Dictionary containing task parameters and data

    Returns:
        TaskRun instance for the started task
    """
    return TaskRun.objects.create(
        agent_name=agent_name,
        payload=payload,
        status='RUNNING'
    )


def record_task_end(task_run: TaskRun, success: bool, error: str = None):
    """
    Record the completion of an agent task execution.

    Args:
        task_run: TaskRun instance returned from record_task_start
        success: True if task completed successfully, False otherwise
        error: Error message if task failed (optional)
    """
    task_run.end_time = timezone.now()
    task_run.status = 'SUCCESS' if success else 'FAILED'

    if error:
        task_run.error_message = error

    task_run.save()
