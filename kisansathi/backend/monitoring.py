"""Monitoring and Metrics for KisanSathi Backend"""

import time
import psutil
import os
from datetime import datetime
from collections import defaultdict

class PerformanceMonitor:
    """Monitor system and application performance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
        self.response_times = []
    
    def record_request(self, endpoint, method, status_code, response_time):
        """Record API request"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        key = f'{method} {endpoint}'
        self.endpoint_stats[key]['count'] += 1
        self.endpoint_stats[key]['total_time'] += response_time
        
        if status_code >= 400:
            self.error_count += 1
            self.endpoint_stats[key]['errors'] += 1
    
    def get_stats(self):
        """Get performance statistics"""
        uptime = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'uptime_seconds': int(uptime),
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            'avg_response_time_ms': round(avg_response_time, 2),
            'requests_per_minute': round(self.request_count / (uptime / 60), 2) if uptime > 0 else 0
        }
    
    def get_endpoint_stats(self):
        """Get per-endpoint statistics"""
        stats = {}
        for endpoint, data in self.endpoint_stats.items():
            avg_time = data['total_time'] / data['count'] if data['count'] > 0 else 0
            stats[endpoint] = {
                'requests': data['count'],
                'avg_response_time_ms': round(avg_time, 2),
                'errors': data['errors']
            }
        return stats

class SystemMonitor:
    """Monitor system resources"""
    
    @staticmethod
    def get_system_stats():
        """Get system resource statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': round(memory.used / (1024*1024), 2),
                'memory_total_mb': round(memory.total / (1024*1024), 2),
                'disk_percent': disk.percent,
                'disk_used_gb': round(disk.used / (1024*1024*1024), 2),
                'disk_total_gb': round(disk.total / (1024*1024*1024), 2)
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_process_stats():
        """Get current process statistics"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                'pid': process.pid,
                'memory_mb': round(memory_info.rss / (1024*1024), 2),
                'cpu_percent': process.cpu_percent(interval=1),
                'num_threads': process.num_threads(),
                'status': process.status()
            }
        except Exception as e:
            return {'error': str(e)}

class HealthCheck:
    """Health check for system components"""
    
    def __init__(self, db=None):
        self.db = db
        self.last_check = None
    
    def check_database(self):
        """Check database connectivity"""
        try:
            if self.db:
                self.db.command('ping')
                return {'status': 'healthy', 'message': 'Database connected'}
            return {'status': 'unknown', 'message': 'Database not configured'}
        except Exception as e:
            return {'status': 'unhealthy', 'message': f'Database error: {str(e)}'}
    
    def check_system(self):
        """Check system health"""
        try:
            stats = SystemMonitor.get_system_stats()
            
            if stats.get('cpu_percent', 0) > 90:
                return {'status': 'warning', 'message': 'High CPU usage'}
            if stats.get('memory_percent', 0) > 90:
                return {'status': 'warning', 'message': 'High memory usage'}
            if stats.get('disk_percent', 0) > 90:
                return {'status': 'warning', 'message': 'Low disk space'}
            
            return {'status': 'healthy', 'message': 'System resources normal'}
        except Exception as e:
            return {'status': 'unknown', 'message': str(e)}
    
    def get_health_status(self):
        """Get overall health status"""
        db_status = self.check_database()
        system_status = self.check_system()
        
        overall = 'healthy'
        if db_status['status'] == 'unhealthy' or system_status['status'] == 'unhealthy':
            overall = 'unhealthy'
        elif db_status['status'] == 'warning' or system_status['status'] == 'warning':
            overall = 'warning'
        
        return {
            'status': overall,
            'timestamp': datetime.now().isoformat(),
            'database': db_status,
            'system': system_status,
            'components': {
                'api': 'running',
                'cache': 'running',
                'rate_limiter': 'running'
            }
        }

# Global instances
performance_monitor = PerformanceMonitor()
system_monitor = SystemMonitor()
