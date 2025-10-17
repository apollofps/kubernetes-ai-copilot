"""
Mock data generator for Kubernetes cluster metrics.
Generates realistic pod data with various resource utilization patterns.
"""

import random
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd


class MockDataGenerator:
    def __init__(self, config_path: str = "config/mock_clusters.yaml"):
        """Initialize the mock data generator with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.namespaces = self.config['namespaces']
        self.workload_types = self.config['workload_types']
        
    def generate_pod_data(self) -> List[Dict[str, Any]]:
        """Generate comprehensive pod data with metrics and issues."""
        pods = []
        
        for namespace in self.namespaces:
            namespace_pods = self._generate_namespace_pods(namespace)
            pods.extend(namespace_pods)
            
        return pods
    
    def _generate_namespace_pods(self, namespace: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate pods for a specific namespace."""
        pods = []
        workload_type = self.workload_types[namespace['workload_type']]
        
        for i in range(namespace['pod_count']):
            pod = self._generate_single_pod(
                namespace['name'], 
                i, 
                workload_type, 
                namespace['issues']
            )
            pods.append(pod)
            
        return pods
    
    def _generate_single_pod(self, namespace: str, index: int, 
                           workload_type: Dict[str, Any], 
                           issues: List[str]) -> Dict[str, Any]:
        """Generate a single pod with realistic metrics."""
        pod_name = f"{namespace}-pod-{index:02d}"
        
        # Generate base resource specs
        cpu_request = random.randint(*workload_type['cpu_request_range'])
        memory_request = random.randint(*workload_type['memory_request_range'])
        
        # Apply issues to create realistic scenarios
        cpu_limit, memory_limit = self._apply_resource_issues(
            cpu_request, memory_request, workload_type, issues
        )
        
        # Generate current usage (should be realistic based on limits)
        cpu_usage, memory_usage = self._generate_usage_metrics(
            cpu_request, memory_limit, issues
        )
        
        # Generate historical data (7 days)
        historical_data = self._generate_historical_metrics(
            cpu_usage, memory_usage, 7
        )
        
        # Calculate efficiency metrics
        cpu_efficiency = (cpu_usage / cpu_request) * 100 if cpu_request > 0 else 0
        memory_efficiency = (memory_usage / memory_request) * 100 if memory_request > 0 else 0
        
        # Generate restart count
        restart_count = self._generate_restart_count(issues, workload_type['restart_threshold'])
        
        return {
            'name': pod_name,
            'namespace': namespace,
            'workload_type': workload_type,
            'resources': {
                'cpu_request': cpu_request,
                'memory_request': memory_request,
                'cpu_limit': cpu_limit,
                'memory_limit': memory_limit,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage
            },
            'efficiency': {
                'cpu_efficiency': round(cpu_efficiency, 2),
                'memory_efficiency': round(memory_efficiency, 2),
                'overall_efficiency': round((cpu_efficiency + memory_efficiency) / 2, 2)
            },
            'restart_count': restart_count,
            'historical_data': historical_data,
            'issues': self._identify_issues(cpu_usage, memory_usage, cpu_request, 
                                          memory_request, cpu_limit, memory_limit, 
                                          restart_count, issues),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
        }
    
    def _apply_resource_issues(self, cpu_request: int, memory_request: int,
                             workload_type: Dict[str, Any], 
                             issues: List[str]) -> tuple:
        """Apply resource issues to create problematic scenarios."""
        cpu_multiplier = random.uniform(*workload_type['cpu_limit_multiplier'])
        memory_multiplier = random.uniform(*workload_type['memory_limit_multiplier'])
        
        # Apply specific issues
        if 'over-provisioned' in issues and random.random() < 0.3:
            cpu_multiplier *= random.uniform(2.0, 4.0)
            memory_multiplier *= random.uniform(2.0, 4.0)
        elif 'under-provisioned' in issues and random.random() < 0.3:
            cpu_multiplier *= random.uniform(1.0, 1.2)
            memory_multiplier *= random.uniform(1.0, 1.2)
        
        cpu_limit = int(cpu_request * cpu_multiplier)
        memory_limit = int(memory_request * memory_multiplier)
        
        return cpu_limit, memory_limit
    
    def _generate_usage_metrics(self, cpu_request: int, memory_limit: int, 
                              issues: List[str]) -> tuple:
        """Generate realistic usage metrics based on requests and issues."""
        # Base usage should be reasonable
        cpu_usage = random.uniform(0.3, 0.8) * cpu_request
        
        # Apply issue-specific usage patterns
        if 'memory-pressure' in issues and random.random() < 0.4:
            memory_usage = random.uniform(0.85, 0.98) * memory_limit
        elif 'resource-waste' in issues and random.random() < 0.3:
            cpu_usage = random.uniform(0.1, 0.3) * cpu_request
            memory_usage = random.uniform(0.1, 0.3) * memory_limit
        else:
            memory_usage = random.uniform(0.4, 0.7) * memory_limit
        
        return int(cpu_usage), int(memory_usage)
    
    def _generate_historical_metrics(self, cpu_usage: int, memory_usage: int, 
                                   days: int) -> List[Dict[str, Any]]:
        """Generate historical metrics for trend analysis."""
        historical = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days * 24):  # Hourly data
            timestamp = base_date + timedelta(hours=i)
            
            # Add some realistic variation
            cpu_variation = random.uniform(0.8, 1.2)
            memory_variation = random.uniform(0.9, 1.1)
            
            historical.append({
                'timestamp': timestamp,
                'cpu_usage': int(cpu_usage * cpu_variation),
                'memory_usage': int(memory_usage * memory_variation)
            })
            
        return historical
    
    def _generate_restart_count(self, issues: List[str], threshold: int) -> int:
        """Generate restart count based on issues."""
        if 'high-restarts' in issues and random.random() < 0.4:
            return random.randint(threshold + 1, threshold + 10)
        elif 'oom-killed' in issues and random.random() < 0.3:
            return random.randint(1, 5)
        else:
            return random.randint(0, threshold)
    
    def _identify_issues(self, cpu_usage: int, memory_usage: int,
                        cpu_request: int, memory_request: int,
                        cpu_limit: int, memory_limit: int,
                        restart_count: int, namespace_issues: List[str]) -> List[str]:
        """Identify specific issues with the pod."""
        issues = []
        
        # Resource utilization issues
        if cpu_usage / cpu_request < 0.3:
            issues.append('low-cpu-utilization')
        if memory_usage / memory_request < 0.3:
            issues.append('low-memory-utilization')
            
        # Resource pressure issues
        if cpu_usage / cpu_limit > 0.9:
            issues.append('high-cpu-pressure')
        if memory_usage / memory_limit > 0.9:
            issues.append('high-memory-pressure')
            
        # Restart issues
        if restart_count > 3:
            issues.append('frequent-restarts')
            
        # Over-provisioning
        if cpu_request > cpu_usage * 2:
            issues.append('over-provisioned-cpu')
        if memory_request > memory_usage * 2:
            issues.append('over-provisioned-memory')
            
        return issues
    
    def get_cluster_summary(self, pods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate cluster-level summary statistics."""
        total_pods = len(pods)
        total_cpu_request = sum(p['resources']['cpu_request'] for p in pods)
        total_memory_request = sum(p['resources']['memory_request'] for p in pods)
        total_cpu_usage = sum(p['resources']['cpu_usage'] for p in pods)
        total_memory_usage = sum(p['resources']['memory_usage'] for p in pods)
        
        # Calculate efficiency scores
        cpu_efficiency = (total_cpu_usage / total_cpu_request * 100) if total_cpu_request > 0 else 0
        memory_efficiency = (total_memory_usage / total_memory_request * 100) if total_memory_request > 0 else 0
        overall_efficiency = (cpu_efficiency + memory_efficiency) / 2
        
        # Count issues
        issue_counts = {}
        for pod in pods:
            for issue in pod['issues']:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        return {
            'total_pods': total_pods,
            'total_cpu_request': total_cpu_request,
            'total_memory_request': total_memory_request,
            'total_cpu_usage': total_cpu_usage,
            'total_memory_usage': total_memory_usage,
            'cpu_efficiency': round(cpu_efficiency, 2),
            'memory_efficiency': round(memory_efficiency, 2),
            'overall_efficiency': round(overall_efficiency, 2),
            'issue_counts': issue_counts,
            'namespaces': list(set(p['namespace'] for p in pods))
        }


def generate_mock_cluster_data() -> tuple:
    """Generate mock cluster data and return pods and summary."""
    generator = MockDataGenerator()
    pods = generator.generate_pod_data()
    summary = generator.get_cluster_summary(pods)
    return pods, summary


if __name__ == "__main__":
    # Test the mock data generator
    pods, summary = generate_mock_cluster_data()
    print(f"Generated {len(pods)} pods across {len(summary['namespaces'])} namespaces")
    print(f"Overall efficiency: {summary['overall_efficiency']}%")
    print(f"Issues found: {summary['issue_counts']}")
