#!/usr/bin/env python3
"""
SAP HANA database monitoring via SQL queries over SSH.
"""

import logging
from typing import Dict, Any
from ssh_client import SSHClient, SSHCommand

logger = logging.getLogger(__name__)


class HANAMonitor:
    """
    Monitors SAP HANA databases.
    """
    
    def __init__(self):
        self.ssh_client = SSHClient()
    
    async def query_hana(
        self,
        hostname: str,
        database: str,
        query: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Execute HQL query against HANA.
        """
        # Example using hdbsql
        cmd = SSHCommand(
            hostname=hostname,
            username=username,
            password=password,
            command=f'hdbsql -d {database} -u SYSTEM -p "***" "{query}"'
        )
        result = await self.ssh_client.execute_command(cmd)
        return result
    
    async def get_backup_catalog(self, hostname: str, database: str,
                                 username: str, password: str) -> Dict[str, Any]:
        """
        Query HANA backup catalog.
        """
        query = "SELECT * FROM SYS.M_BACKUP_CATALOG ORDER BY START_TIME DESC LIMIT 10"
        result = await self.query_hana(hostname, database, query, username, password)
        return result
    
    async def get_memory_usage(self, hostname: str, database: str,
                               username: str, password: str) -> Dict[str, Any]:
        """
        Query HANA memory usage.
        """
        query = "SELECT HOST, USED_MEMORY_GB, ALLOCATION_LIMIT_GB FROM SYS.M_HOST_RESOURCE_UTILIZATION"
        result = await self.query_hana(hostname, database, query, username, password)
        return result
    
    async def get_expensive_statements(self, hostname: str, database: str,
                                      username: str, password: str) -> Dict[str, Any]:
        """
        Get expensive/long-running SQL statements.
        """
        query = "SELECT TOP 10 * FROM SYS.M_EXPENSIVE_STATEMENTS ORDER BY DURATION DESC"
        result = await self.query_hana(hostname, database, query, username, password)
        return result
