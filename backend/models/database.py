#!/usr/bin/env python3
"""
SQLAlchemy ORM models for SAP Infrastructure Monitoring Platform.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, UniqueConstraint, Index, LargeBinary, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class Server(Base):
    """
    Server entity - represents SAP systems, HANA databases, etc.
    """
    __tablename__ = "servers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sid = Column(String(3), nullable=False, index=True)
    hostname = Column(String(255), nullable=False, unique=True)
    system_type = Column(String(50), nullable=False)  # ECC, S/4HANA, BW
    db_type = Column(String(50), nullable=False)  # HANA, ASE, Oracle
    backup_path = Column(String(500))
    ssh_host = Column(String(255), nullable=False)
    ssh_user = Column(String(100), nullable=False)
    ssh_password_encrypted = Column(String(500))
    ssh_key_path = Column(String(500))
    ssh_port = Column(Integer, default=22)
    enabled = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    metrics = relationship("Metric", back_populates="server", cascade="all, delete-orphan")
    processes = relationship("SAPProcess", back_populates="server", cascade="all, delete-orphan")
    filesystems = relationship("Filesystem", back_populates="server", cascade="all, delete-orphan")
    hana_backups = relationship("HANABackup", back_populates="server", cascade="all, delete-orphan")
    nas_mounts = relationship("NASMount", back_populates="server", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="server", cascade="all, delete-orphan")
    ai_analysis = relationship("AIAnalysis", back_populates="server", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_sid_enabled', 'sid', 'enabled'),
    )


class Metric(Base):
    """
    Time-series metrics for servers (OS performance data).
    Optimized for TimescaleDB hypertable.
    """
    __tablename__ = "metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    time = Column(DateTime, nullable=False, index=True)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    
    # CPU Metrics
    cpu_usage = Column(Float)  # percentage
    cpu_load = Column(Float)  # load average
    cpu_wait = Column(Float)  # percentage
    cpu_steal = Column(Float)  # percentage
    
    # Memory Metrics
    memory_usage = Column(Float)  # MB
    memory_available = Column(Float)  # MB
    memory_cached = Column(Float)  # MB
    swap_used = Column(Float)  # MB
    oom_events = Column(Integer, default=0)
    
    # Network Metrics
    network_in = Column(Float)  # bytes
    network_out = Column(Float)  # bytes
    network_packets_in = Column(Integer)
    network_packets_out = Column(Integer)
    
    # Disk I/O Metrics
    disk_io_read = Column(Float)  # IOPS
    disk_io_write = Column(Float)  # IOPS
    disk_io_read_bytes = Column(Float)  # MB/s
    disk_io_write_bytes = Column(Float)  # MB/s
    
    # Process Metrics
    process_count = Column(Integer)
    thread_count = Column(Integer)
    
    # Server relationship
    server = relationship("Server", back_populates="metrics")
    
    __table_args__ = (
        Index('idx_metrics_server_time', 'server_id', 'time'),
    )


class Filesystem(Base):
    """
    Filesystem and mount point monitoring.
    """
    __tablename__ = "filesystems"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    mount_point = Column(String(500), nullable=False)
    filesystem_type = Column(String(50))  # ext4, xfs, nfs, etc.
    device = Column(String(255))
    total_size = Column(Integer)  # KB
    used_size = Column(Integer)  # KB
    available_size = Column(Integer)  # KB
    inode_total = Column(Integer)
    inode_used = Column(Integer)
    inode_free = Column(Integer)
    last_checked = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    server = relationship("Server", back_populates="filesystems")
    
    __table_args__ = (
        UniqueConstraint('server_id', 'mount_point', name='uq_server_mount'),
        Index('idx_filesystem_server_mount', 'server_id', 'mount_point'),
    )


class SAPProcess(Base):
    """
    SAP process status and resource monitoring.
    """
    __tablename__ = "sap_processes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    process_name = Column(String(100), nullable=False)  # dispatcher, gateway, enqueue, msg_server
    status = Column(String(50), nullable=False)  # running, stopped, crashed
    pid = Column(Integer)
    memory_mb = Column(Float)
    cpu_percent = Column(Float)
    uptime_seconds = Column(Integer)
    restart_count = Column(Integer, default=0)
    last_checked = Column(DateTime, default=datetime.utcnow)
    last_status_change = Column(DateTime)
    
    # Relationship
    server = relationship("Server", back_populates="processes")
    
    __table_args__ = (
        Index('idx_process_server_name', 'server_id', 'process_name'),
    )


class HANABackup(Base):
    """
    HANA backup catalog monitoring.
    """
    __tablename__ = "hana_backups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    backup_id = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(50), nullable=False)  # SUCCESS, FAILED, IN_PROGRESS
    backup_type = Column(String(50))  # FULL, INCREMENTAL, DIFFERENTIAL
    backup_size_gb = Column(Float)
    data_backed_up_gb = Column(Float)
    catalog_size_gb = Column(Float)
    throughput_mbs = Column(Float)
    backup_path = Column(String(500))
    error_message = Column(Text)
    
    # Relationship
    server = relationship("Server", back_populates="hana_backups")
    
    __table_args__ = (
        Index('idx_backup_server_status', 'server_id', 'status'),
        Index('idx_backup_server_time', 'server_id', 'start_time'),
    )


class NASMount(Base):
    """
    NAS mount and backup storage monitoring.
    """
    __tablename__ = "nas_mounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    mount_path = Column(String(500), nullable=False)
    nfs_server = Column(String(255), nullable=False)
    nfs_share = Column(String(500))
    status = Column(String(50), nullable=False)  # mounted, unmounted, timeout, error
    latency_ms = Column(Float)
    available_gb = Column(Float)
    used_gb = Column(Float)
    total_gb = Column(Float)
    last_response_time = Column(DateTime, default=datetime.utcnow)
    last_error = Column(Text)
    
    # Relationship
    server = relationship("Server", back_populates="nas_mounts")
    
    __table_args__ = (
        UniqueConstraint('server_id', 'mount_path', name='uq_server_nas_mount'),
        Index('idx_nas_server_status', 'server_id', 'status'),
    )


class Alert(Base):
    """
    Alert management for monitoring events.
    """
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    severity = Column(String(50), nullable=False, index=True)  # INFO, WARNING, CRITICAL
    alert_type = Column(String(100), nullable=False)  # CPU_HIGH, DISK_FULL, BACKUP_FAILED, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default='NEW', index=True)  # NEW, ACKNOWLEDGED, RESOLVED, SUPPRESSED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    resolution_notes = Column(Text)
    
    # Relationship
    server = relationship("Server", back_populates="alerts")
    
    __table_args__ = (
        Index('idx_alert_severity_status', 'severity', 'status'),
        Index('idx_alert_server_created', 'server_id', 'created_at'),
    )


class AIAnalysis(Base):
    """
    AI-generated analysis and insights.
    """
    __tablename__ = "ai_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey('servers.id'), nullable=False)
    analysis_type = Column(String(100), nullable=False)  # RCA, PREDICTION, SUMMARY, CORRELATION
    title = Column(String(255))
    summary = Column(Text, nullable=False)
    confidence_score = Column(Float)  # 0.0 to 1.0
    correlated_metrics = Column(JSONB)  # JSON array of correlated metrics
    recommendations = Column(JSONB)  # JSON array of recommended actions
    related_alerts = Column(JSONB)  # JSON array of related alert IDs
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)  # Auto-expire old analyses
    
    # Relationship
    server = relationship("Server", back_populates="ai_analysis")
    
    __table_args__ = (
        Index('idx_analysis_server_type', 'server_id', 'analysis_type'),
        Index('idx_analysis_created', 'created_at'),
    )


class User(Base):
    """
    User accounts for RBAC (Role-Based Access Control).
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(500), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False, default='viewer')  # admin, basis_team, infra_team, viewer
    enabled = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """
    Audit logging for compliance and security tracking.
    """
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # CREATE, UPDATE, DELETE, etc.
    resource_type = Column(String(100), nullable=False)  # server, alert, etc.
    resource_id = Column(UUID(as_uuid=True))
    changes = Column(JSONB)  # JSON object of before/after changes
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_action_resource', 'action', 'resource_type'),
    )
