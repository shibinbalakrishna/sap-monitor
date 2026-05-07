#!/usr/bin/env python3
"""
SAP system monitoring via sapcontrol and SSH.
"""

import logging
from typing import Dict, Any, List
from ssh_client import SSHClient, SSHCommand

logger = logging.getLogger(__name__)


class SAPMonitor:
    """
    Monitors SAP instances (ECC, S/4HANA, BW) using sapcontrol.
    """
    
    def __init__(self):
        self.ssh_client = SSHClient()
    
    async def get_process_list(self, hostname: str, sid: str, instance_num: str, 
                               username: str, password: str) -> Dict[str, Any]:
        """
        Get SAP process list using sapcontrol.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command=f"/usr/sap/{sid}/{instance_num}/exe/sapcontrol -nr {instance_num} -function GetProcessList 2>/dev/null"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def get_system_info(self, hostname: str, sid: str, instance_num: str,
                              username: str, password: str) -> Dict[str, Any]:
        """
        Get SAP system information.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command=f"/usr/sap/{sid}/{instance_num}/exe/sapcontrol -nr {instance_num} -function GetSystemInstanceList 2>/dev/null"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def get_gateway_status(self, hostname: str, sid: str, instance_num: str,
                                 username: str, password: str) -> Dict[str, Any]:
        """
        Check SAP gateway connectivity.
        """
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command=f"netstat -tnp 2>/dev/null | grep -i gateway | wc -l"
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
