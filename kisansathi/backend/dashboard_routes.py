"""Dashboard and Monitoring Routes"""

from flask import Blueprint, jsonify
from datetime import datetime
from monitoring import performance_monitor, system_monitor, HealthCheck

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'performance': performance_monitor.get_stats(),
        'system': system_monitor.get_system_stats(),
        'process': system_monitor.get_process_stats()
    }), 200

@dashboard_bp.route('/endpoints', methods=['GET'])
def get_endpoint_stats():
    """Get per-endpoint statistics"""
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'endpoints': performance_monitor.get_endpoint_stats()
    }), 200

@dashboard_bp.route('/health', methods=['GET'])
def get_health():
    """Get system health status"""
    health_check = HealthCheck()
    return jsonify(health_check.get_health_status()), 200

@dashboard_bp.route('/logs/recent', methods=['GET'])
def get_recent_logs():
    """Get recent logs"""
    import os
    import logging
    
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    logs = []
    
    try:
        if os.path.exists(log_dir):
            for filename in sorted(os.listdir(log_dir), reverse=True)[:3]:
                filepath = os.path.join(log_dir, filename)
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as f:
                        lines = f.readlines()[-50:]  # Last 50 lines
                        logs.append({
                            'file': filename,
                            'lines': lines
                        })
    except Exception as e:
        logs = [{'error': str(e)}]
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'logs': logs
    }), 200

@dashboard_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get system alerts"""
    health = HealthCheck()
    health_status = health.get_health_status()
    
    alerts = []
    
    # Check for warnings
    if health_status['database']['status'] != 'healthy':
        alerts.append({
            'type': 'database',
            'severity': 'high' if health_status['database']['status'] == 'unhealthy' else 'medium',
            'message': health_status['database']['message']
        })
    
    if health_status['system']['status'] != 'healthy':
        alerts.append({
            'type': 'system',
            'severity': 'high' if health_status['system']['status'] == 'unhealthy' else 'medium',
            'message': health_status['system']['message']
        })
    
    # Check performance
    stats = performance_monitor.get_stats()
    if stats['error_rate'] > 5:
        alerts.append({
            'type': 'performance',
            'severity': 'medium',
            'message': f"High error rate: {stats['error_rate']:.2f}%"
        })
    
    if stats['avg_response_time_ms'] > 1000:
        alerts.append({
            'type': 'performance',
            'severity': 'low',
            'message': f"Slow response time: {stats['avg_response_time_ms']:.2f}ms"
        })
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'alerts': alerts,
        'alert_count': len(alerts)
    }), 200

@dashboard_bp.route('/summary', methods=['GET'])
def get_summary():
    """Get dashboard summary"""
    health = HealthCheck()
    stats = performance_monitor.get_stats()
    system_stats = system_monitor.get_system_stats()
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'status': health.get_health_status()['status'],
        'uptime_hours': round(stats['uptime_seconds'] / 3600, 2),
        'total_requests': stats['total_requests'],
        'error_rate': f"{stats['error_rate']:.2f}%",
        'avg_response_time': f"{stats['avg_response_time_ms']:.2f}ms",
        'cpu_usage': f"{system_stats.get('cpu_percent', 0):.1f}%",
        'memory_usage': f"{system_stats.get('memory_percent', 0):.1f}%",
        'disk_usage': f"{system_stats.get('disk_percent', 0):.1f}%"
    }), 200
