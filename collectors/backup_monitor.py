#!/usr/bin/env python3
"""
NAS backup mount and backup job monitoring.
"""

import logging
from typing import Dict, Any
from ssh_client import SSHClient, SSHCommand

logger = logging.getLogger(__name__)


class BackupMonitor:
    """
    Monitors NAS mounts and backup jobs.
    """
    
    def __init__(self):
        self.ssh_client = SSHClient()
    
    async def check_nas_mount(self, hostname: str, mount_path: str,
                             username: str, password: str) -> Dict[str, Any]:
        """
        Check NAS mount availability and latency.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command=f"test -d {mount_path} && echo 'mounted' || echo 'unmounted'; df -h {mount_path} 2>/dev/null; time ls {mount_path} 2>/dev/null | head -1"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def get_backup_stats(self, hostname: str, backup_path: str,
                              username: str, password: str) -> Dict[str, Any]:
        """
        Get backup directory statistics.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command=f"du -sh {backup_path}/* 2>/dev/null | sort -hr && ls -lh {backup_path} 2>/dev/null | tail -5"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def check_backup_completion(self, hostname: str, backup_path: str,
                                     username: str, password: str) -> Dict[str, Any]:
        """
        Check last backup completion status.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command=f"ls -lt {backup_path}/* 2>/dev/null | head -3 && find {backup_path} -name '*.log' -mtime -1 -exec tail -5 {{}} \\;"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
