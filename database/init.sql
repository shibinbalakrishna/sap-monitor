-- SAP Infrastructure Monitoring Platform - Database Schema
-- PostgreSQL 15 + TimescaleDB

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Servers table - System inventory
CREATE TABLE IF NOT EXISTS servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sid VARCHAR(3) NOT NULL UNIQUE,
    hostname VARCHAR(255) NOT NULL UNIQUE,
    system_type VARCHAR(50) NOT NULL,
    db_type VARCHAR(50) NOT NULL,
    backup_path VARCHAR(500),
    ssh_host VARCHAR(255) NOT NULL,
    ssh_user VARCHAR(100) NOT NULL,
    ssh_password_encrypted VARCHAR(500),
    ssh_key_path VARCHAR(500),
    ssh_port INT DEFAULT 22,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_servers_sid ON servers(sid);
CREATE INDEX idx_servers_enabled ON servers(enabled);
CREATE INDEX idx_servers_sid_enabled ON servers(sid, enabled);

-- Metrics table - TimescaleDB hypertable for time-series data
CREATE TABLE IF NOT EXISTS metrics (
    id UUID DEFAULT gen_random_uuid(),
    time TIMESTAMP NOT NULL,
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    cpu_usage FLOAT,
    cpu_load FLOAT,
    cpu_wait FLOAT,
    cpu_steal FLOAT,
    memory_usage FLOAT,
    memory_available FLOAT,
    memory_cached FLOAT,
    swap_used FLOAT,
    oom_events INT DEFAULT 0,
    network_in FLOAT,
    network_out FLOAT,
    network_packets_in INT,
    network_packets_out INT,
    disk_io_read FLOAT,
    disk_io_write FLOAT,
    disk_io_read_bytes FLOAT,
    disk_io_write_bytes FLOAT,
    process_count INT,
    thread_count INT
);

SELECT create_hypertable('metrics', 'time', if_not_exists => TRUE);
SELECT set_integer_now_func('metrics', 'extract(epoch from now())::bigint', replace_if_exists => true);

CREATE INDEX idx_metrics_server_time ON metrics(server_id, time DESC);
CREATE INDEX idx_metrics_time ON metrics(time DESC);

-- Implement retention policy (30 days)
SELECT add_retention_policy('metrics', INTERVAL '30 days', if_not_exists => TRUE);

-- Filesystems table
CREATE TABLE IF NOT EXISTS filesystems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    mount_point VARCHAR(500) NOT NULL,
    filesystem_type VARCHAR(50),
    device VARCHAR(255),
    total_size BIGINT,
    used_size BIGINT,
    available_size BIGINT,
    inode_total BIGINT,
    inode_used BIGINT,
    inode_free BIGINT,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(server_id, mount_point)
);

CREATE INDEX idx_filesystems_server_mount ON filesystems(server_id, mount_point);

-- SAP Processes table
CREATE TABLE IF NOT EXISTS sap_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    process_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    pid INT,
    memory_mb FLOAT,
    cpu_percent FLOAT,
    uptime_seconds INT,
    restart_count INT DEFAULT 0,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_status_change TIMESTAMP
);

CREATE INDEX idx_sap_processes_server_name ON sap_processes(server_id, process_name);

-- HANA Backups table
CREATE TABLE IF NOT EXISTS hana_backups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    backup_id VARCHAR(100) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    backup_type VARCHAR(50),
    backup_size_gb FLOAT,
    data_backed_up_gb FLOAT,
    catalog_size_gb FLOAT,
    throughput_mbs FLOAT,
    backup_path VARCHAR(500),
    error_message TEXT
);

CREATE INDEX idx_hana_backups_server_status ON hana_backups(server_id, status);
CREATE INDEX idx_hana_backups_server_time ON hana_backups(server_id, start_time DESC);

-- NAS Mounts table
CREATE TABLE IF NOT EXISTS nas_mounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    mount_path VARCHAR(500) NOT NULL,
    nfs_server VARCHAR(255) NOT NULL,
    nfs_share VARCHAR(500),
    status VARCHAR(50) NOT NULL,
    latency_ms FLOAT,
    available_gb FLOAT,
    used_gb FLOAT,
    total_gb FLOAT,
    last_response_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_error TEXT,
    UNIQUE(server_id, mount_path)
);

CREATE INDEX idx_nas_mounts_server_status ON nas_mounts(server_id, status);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID REFERENCES servers(id) ON DELETE CASCADE,
    severity VARCHAR(50) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'NEW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    acknowledged_by VARCHAR(100),
    resolution_notes TEXT
);

CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity_status ON alerts(severity, status);
CREATE INDEX idx_alerts_server_created ON alerts(server_id, created_at DESC);

-- AI Analysis table
CREATE TABLE IF NOT EXISTS ai_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100) NOT NULL,
    title VARCHAR(255),
    summary TEXT NOT NULL,
    confidence_score FLOAT,
    correlated_metrics JSONB,
    recommendations JSONB,
    related_alerts JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_ai_analysis_server_type ON ai_analysis(server_id, analysis_type);
CREATE INDEX idx_ai_analysis_created ON ai_analysis(created_at DESC);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(500) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    enabled BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_enabled ON users(enabled);

-- Audit Logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    changes JSONB,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_timestamp ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_logs_action_resource ON audit_logs(action, resource_type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Create default admin user (password: admin123 - CHANGE IN PRODUCTION)
INSERT INTO users (username, email, password_hash, role, enabled)
VALUES (
    'admin',
    'admin@sap-monitor.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmqKJBy',
    'admin',
    true
)
ON CONFLICT (username) DO NOTHING;

-- Create sample basis_team user
INSERT INTO users (username, email, password_hash, role, enabled)
VALUES (
    'basis_user',
    'basis@sap-monitor.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmqKJBy',
    'basis_team',
    true
)
ON CONFLICT (username) DO NOTHING;

COMMIT;
