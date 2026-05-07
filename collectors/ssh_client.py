#!/usr/bin/env python3
"""
AsyncSSH client wrapper for parallel SSH execution to SAP servers.
"""

import asyncio
import asyncssh
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class SSHCommand:
    """
    SSH command execution parameters.
    """
    hostname: str
    command: str
    username: str
    password: Optional[str] = None
    key_filename: Optional[str] = None
    port: int = 22
    timeout: int = 10


class SSHClient:
    """
    AsyncSSH client for parallel execution of monitoring commands.
    """
    
    def __init__(self):
        self.timeout = settings.SSH_TIMEOUT
        self.retries = settings.SSH_RETRIES
        
    async def execute_command(self, cmd: SSHCommand) -> Dict[str, Any]:
        """
        Execute a single SSH command with error handling and retries.
        
        Args:
            cmd: SSHCommand with connection and command details
            
        Returns:
            dict: Command output and metadata
        """
        for attempt in range(self.retries):
            try:
                async with asyncssh.connect(
                    cmd.hostname,
                    port=cmd.port,
                    username=cmd.username,
                    password=cmd.password,
                    known_hosts=None,
                    client_keys=[cmd.key_filename] if cmd.key_filename else None,
                ) as conn:
                    result = await asyncio.wait_for(
                        conn.run(cmd.command),
                        timeout=cmd.timeout
                    )
                    
                    return {
                        "status": "success",
                        "hostname": cmd.hostname,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "exit_code": result.exit_status,
                        "attempt": attempt + 1
                    }
                    
            except asyncio.TimeoutError:
                logger.warning(f"SSH timeout on {cmd.hostname} (attempt {attempt + 1}/{self.retries})")
                if attempt == self.retries - 1:
                    return {
                        "status": "timeout",
                        "hostname": cmd.hostname,
                        "error": f"SSH command timeout after {cmd.timeout}s",
                        "attempt": attempt + 1
                    }
                    
            except asyncssh.SSHError as e:
                logger.error(f"SSH error on {cmd.hostname}: {str(e)} (attempt {attempt + 1}/{self.retries})")
                if attempt == self.retries - 1:
                    return {
                        "status": "error",
                        "hostname": cmd.hostname,
                        "error": str(e),
                        "attempt": attempt + 1
                    }
                    
            except Exception as e:
                logger.error(f"Unexpected error on {cmd.hostname}: {str(e)}")
                if attempt == self.retries - 1:
                    return {
                        "status": "error",
                        "hostname": cmd.hostname,
                        "error": str(e),
                        "attempt": attempt + 1
                    }
            
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def execute_batch(
        self,
        commands: List[SSHCommand],
        max_concurrent: int = settings.SSH_PARALLEL_WORKERS
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple SSH commands in parallel with concurrency limit.
        
        Args:
            commands: List of SSHCommand objects
            max_concurrent: Maximum concurrent SSH connections
            
        Returns:
            list: Results from all commands
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_execute(cmd: SSHCommand):
            async with semaphore:
                return await self.execute_command(cmd)
        
        results = await asyncio.gather(*[limited_execute(cmd) for cmd in commands])
        return results
    
    async def validate_connection(self, cmd: SSHCommand) -> bool:
        """
        Validate SSH connectivity to a host.
        
        Args:
            cmd: SSHCommand with connection details
            
        Returns:
            bool: True if connection successful
        """
        try:
            async with asyncio.timeout(self.timeout):
                async with asyncssh.connect(
                    cmd.hostname,
                    port=cmd.port,
                    username=cmd.username,
                    password=cmd.password,
                    known_hosts=None,
                ) as conn:
                    return True
        except Exception as e:
            logger.error(f"Connection validation failed for {cmd.hostname}: {str(e)}")
            return False
