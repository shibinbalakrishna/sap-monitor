#!/usr/bin/env python3
"""
Linux OS metrics collection via SSH.
"""

import logging
from typing import Dict, Any
from ssh_client import SSHClient, SSHCommand

logger = logging.getLogger(__name__)


class OSMetricsCollector:
    """
    Collects Linux OS metrics (CPU, memory, disk, network).
    """
    
    def __init__(self):
        self.ssh_client = SSHClient()
    
    async def collect_cpu_metrics(self, hostname: str, username: str, password: str) -> Dict[str, Any]:
        """
        Collect CPU metrics using top and mpstat.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command="top -bn1 | head -3 && mpstat -u 1 1 2>/dev/null | tail -1"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def collect_memory_metrics(self, hostname: str, username: str, password: str) -> Dict[str, Any]:
        """
        Collect memory metrics.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command="free -b && vmstat 1 2 | tail -1"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def collect_disk_metrics(self, hostname: str, username: str, password: str) -> Dict[str, Any]:
        """
        Collect disk and filesystem metrics.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command="df -B1 && df -i"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def collect_network_metrics(self, hostname: str, username: str, password: str) -> Dict[str, Any]:
        """
        Collect network metrics.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command="cat /proc/net/dev && ss -s"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def collect_process_metrics(self, hostname: str, username: str, password: str) -> Dict[str, Any]:
        """
        Collect process and thread count.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command="ps -ef | wc -l && grep -c ^processor /proc/cpuinfo"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
