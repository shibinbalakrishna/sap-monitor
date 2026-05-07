#!/usr/bin/env python3
"""
APScheduler configuration for automated monitoring tasks.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config.settings import settings

logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """
    Manages scheduled monitoring tasks.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def add_job(self, func, job_id: str, interval_seconds: int = settings.SCHEDULER_INTERVAL_SECONDS):
        """
        Add a scheduled job.
        
        Args:
            func: Async function to schedule
            job_id: Unique job identifier
            interval_seconds: Interval between executions
        """
        self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id=job_id,
            name=job_id,
            replace_existing=True,
            max_instances=settings.SCHEDULER_MAX_INSTANCES
        )
        logger.info(f"Scheduled job: {job_id} (interval: {interval_seconds}s)")
    
    async def start(self):
        """
        Start the scheduler.
        """
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Monitoring scheduler started")
    
    async def stop(self):
        """
        Stop the scheduler.
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Monitoring scheduler stopped")
    
    def get_jobs(self):
        """
        Get all scheduled jobs.
        """
        return self.scheduler.get_jobs()
