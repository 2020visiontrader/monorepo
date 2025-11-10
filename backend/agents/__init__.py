"""
Background Automation Agents for E-Commerce Platform

This package contains specialized automation agents that handle background processing,
scheduled tasks, and complex workflows for different business domains.

Agent Architecture:
    - Each agent focuses on a specific business domain (brands, AI, competitors, etc.)
    - Agents use TaskRun logging for execution tracking and monitoring
    - Supabase Storage integration for asset management and file operations
    - Idempotent operations to prevent duplicate processing
    - Comprehensive error handling with retry logic and alerting

Available Agents:
    - brands_agent: Brand onboarding, profile management, asset processing
    - ai_agent: Content generation, AI model management, quality validation
    - competitors_agent: Competitive analysis, market monitoring, intelligence gathering

Common Patterns:
    - All agents use record_task_start() and record_task_end() for logging
    - Supabase storage operations via upload_file_bytes() and download_file_bytes()
    - Database operations are wrapped in transactions for consistency
    - Failed operations are logged and may trigger alerts for manual intervention

Usage:
    # Run specific agent
    from agents.brands_agent import process_brand_onboarding
    process_brand_onboarding()

    # Run via management command
    python manage.py run_brand_onboarding

    # Check agent execution logs
    TaskRun.objects.filter(agent_name='brands_agent').order_by('-start_time')
"""
