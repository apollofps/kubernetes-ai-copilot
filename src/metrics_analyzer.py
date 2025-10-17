"""
Metrics analyzer for Kubernetes cluster resource optimization.
Analyzes pod metrics and identifies optimization opportunities.
"""

from typing import Dict, List, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta


class MetricsAnalyzer:
    def __init__(self):
        """Initialize the metrics analyzer."""
        self.severity_thresholds = {
            'critical': 0.9,  # 90%+ utilization or frequent restarts
            'warning': 0.7,   # 70%+ utilization or moderate issues
            'info': 0.5       # 50%+ utilization or minor issues
        }
    
    def analyze_pod_metrics(self, pod: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single pod's metrics and return optimization recommendations."""
        resources = pod['resources']
        efficiency = pod['efficiency']
        issues = pod['issues']
        
        analysis = {
            'pod_name': pod['name'],
            'namespace': pod['namespace'],
            'severity': self._calculate_severity(pod),
            'issues': issues,
            'recommendations': [],
            'potential_savings': self._calculate_potential_savings(pod),
            'risk_factors': self._identify_risk_factors(pod)
        }
        
        # Generate specific recommendations based on issues
        analysis['recommendations'] = self._generate_recommendations(pod)
        
        return analysis
    
    def _calculate_severity(self, pod: Dict[str, Any]) -> str:
        """Calculate the severity level of issues for a pod."""
        resources = pod['resources']
        restart_count = pod['restart_count']
        issues = pod['issues']
        
        # Critical conditions
        if (restart_count > 5 or 
            'high-cpu-pressure' in issues or 
            'high-memory-pressure' in issues or
            'oom-killed' in issues):
            return 'critical'
        
        # Warning conditions
        if (restart_count > 2 or
            'frequent-restarts' in issues or
            resources['cpu_usage'] / resources['cpu_limit'] > 0.8 or
            resources['memory_usage'] / resources['memory_limit'] > 0.8):
            return 'warning'
        
        # Info level
        if (len(issues) > 0 or
            resources['cpu_usage'] / resources['cpu_limit'] > 0.6 or
            resources['memory_usage'] / resources['memory_limit'] > 0.6):
            return 'info'
        
        return 'healthy'
    
    def _calculate_potential_savings(self, pod: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential resource savings for a pod."""
        resources = pod['resources']
        issues = pod['issues']
        
        cpu_savings = 0
        memory_savings = 0
        
        # Calculate savings from over-provisioning
        if 'over-provisioned-cpu' in issues:
            # Suggest reducing CPU request to 1.5x current usage
            suggested_cpu = int(resources['cpu_usage'] * 1.5)
            cpu_savings = max(0, resources['cpu_request'] - suggested_cpu)
        
        if 'over-provisioned-memory' in issues:
            # Suggest reducing memory request to 1.3x current usage
            suggested_memory = int(resources['memory_usage'] * 1.3)
            memory_savings = max(0, resources['memory_request'] - suggested_memory)
        
        # Calculate cost savings (rough estimates)
        cpu_cost_per_millicore = 0.001  # $0.001 per millicore per hour
        memory_cost_per_mb = 0.0001     # $0.0001 per MB per hour
        
        hourly_savings = (cpu_savings * cpu_cost_per_millicore + 
                         memory_savings * memory_cost_per_mb)
        monthly_savings = hourly_savings * 24 * 30
        
        return {
            'cpu_savings_millicores': cpu_savings,
            'memory_savings_mb': memory_savings,
            'hourly_cost_savings': round(hourly_savings, 4),
            'monthly_cost_savings': round(monthly_savings, 2)
        }
    
    def _identify_risk_factors(self, pod: Dict[str, Any]) -> List[str]:
        """Identify risk factors for the pod."""
        risks = []
        resources = pod['resources']
        restart_count = pod['restart_count']
        
        # Resource pressure risks
        if resources['cpu_usage'] / resources['cpu_limit'] > 0.8:
            risks.append('CPU throttling risk')
        if resources['memory_usage'] / resources['memory_limit'] > 0.8:
            risks.append('OOMKill risk')
        
        # Stability risks
        if restart_count > 3:
            risks.append('Service instability')
        
        # Efficiency risks
        if pod['efficiency']['cpu_efficiency'] < 30:
            risks.append('Resource waste')
        if pod['efficiency']['memory_efficiency'] < 30:
            risks.append('Memory waste')
        
        return risks
    
    def _generate_recommendations(self, pod: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific recommendations for pod optimization."""
        recommendations = []
        resources = pod['resources']
        issues = pod['issues']
        
        # CPU recommendations
        if 'over-provisioned-cpu' in issues:
            suggested_cpu = int(resources['cpu_usage'] * 1.5)
            recommendations.append({
                'type': 'cpu_request',
                'current': resources['cpu_request'],
                'recommended': suggested_cpu,
                'reason': 'CPU request is significantly higher than actual usage',
                'impact': 'Reduce resource waste and improve cluster efficiency'
            })
        
        if 'high-cpu-pressure' in issues:
            suggested_cpu_limit = int(resources['cpu_usage'] * 1.2)
            recommendations.append({
                'type': 'cpu_limit',
                'current': resources['cpu_limit'],
                'recommended': suggested_cpu_limit,
                'reason': 'CPU usage is approaching the limit',
                'impact': 'Prevent CPU throttling and improve performance'
            })
        
        # Memory recommendations
        if 'over-provisioned-memory' in issues:
            suggested_memory = int(resources['memory_usage'] * 1.3)
            recommendations.append({
                'type': 'memory_request',
                'current': resources['memory_request'],
                'recommended': suggested_memory,
                'reason': 'Memory request is significantly higher than actual usage',
                'impact': 'Reduce memory waste and improve cluster efficiency'
            })
        
        if 'high-memory-pressure' in issues:
            suggested_memory_limit = int(resources['memory_usage'] * 1.2)
            recommendations.append({
                'type': 'memory_limit',
                'current': resources['memory_limit'],
                'recommended': suggested_memory_limit,
                'reason': 'Memory usage is approaching the limit',
                'impact': 'Prevent OOMKill and improve stability'
            })
        
        # Restart recommendations
        if 'frequent-restarts' in issues:
            recommendations.append({
                'type': 'investigation',
                'current': pod['restart_count'],
                'recommended': 'Investigate logs',
                'reason': 'Pod is restarting frequently',
                'impact': 'Improve service reliability and reduce downtime'
            })
        
        return recommendations
    
    def analyze_cluster_metrics(self, pods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cluster-wide metrics and provide optimization insights."""
        analyses = [self.analyze_pod_metrics(pod) for pod in pods]
        
        # Aggregate statistics
        total_pods = len(pods)
        severity_counts = {'critical': 0, 'warning': 0, 'info': 0, 'healthy': 0}
        total_savings = {'cpu': 0, 'memory': 0, 'monthly_cost': 0}
        
        for analysis in analyses:
            severity_counts[analysis['severity']] += 1
            savings = analysis['potential_savings']
            total_savings['cpu'] += savings['cpu_savings_millicores']
            total_savings['memory'] += savings['memory_savings_mb']
            total_savings['monthly_cost'] += savings['monthly_cost_savings']
        
        # Calculate efficiency scores
        cpu_efficiency = sum(p['efficiency']['cpu_efficiency'] for p in pods) / total_pods
        memory_efficiency = sum(p['efficiency']['memory_efficiency'] for p in pods) / total_pods
        overall_efficiency = (cpu_efficiency + memory_efficiency) / 2
        
        # Identify top optimization opportunities
        top_opportunities = sorted(analyses, 
                                 key=lambda x: x['potential_savings']['monthly_cost_savings'], 
                                 reverse=True)[:5]
        
        return {
            'total_pods': total_pods,
            'severity_distribution': severity_counts,
            'efficiency_metrics': {
                'cpu_efficiency': round(cpu_efficiency, 2),
                'memory_efficiency': round(memory_efficiency, 2),
                'overall_efficiency': round(overall_efficiency, 2)
            },
            'potential_savings': {
                'cpu_savings_millicores': int(total_savings['cpu']),
                'memory_savings_mb': int(total_savings['memory']),
                'monthly_cost_savings': round(total_savings['monthly_cost'], 2)
            },
            'top_optimization_opportunities': [
                {
                    'pod_name': opp['pod_name'],
                    'namespace': opp['namespace'],
                    'severity': opp['severity'],
                    'monthly_savings': opp['potential_savings']['monthly_cost_savings']
                }
                for opp in top_opportunities
            ],
            'detailed_analyses': analyses
        }
    
    def get_efficiency_score(self, pod: Dict[str, Any]) -> float:
        """Calculate an overall efficiency score for a pod (0-100)."""
        cpu_efficiency = pod['efficiency']['cpu_efficiency']
        memory_efficiency = pod['efficiency']['memory_efficiency']
        restart_penalty = min(pod['restart_count'] * 5, 20)  # Max 20 point penalty
        
        base_score = (cpu_efficiency + memory_efficiency) / 2
        efficiency_score = max(0, base_score - restart_penalty)
        
        return round(efficiency_score, 2)
    
    def filter_pods_by_severity(self, analyses: List[Dict[str, Any]], 
                               severity: str) -> List[Dict[str, Any]]:
        """Filter pod analyses by severity level."""
        if severity == 'all':
            return analyses
        return [analysis for analysis in analyses if analysis['severity'] == severity]
    
    def filter_pods_by_namespace(self, analyses: List[Dict[str, Any]], 
                                namespace: str) -> List[Dict[str, Any]]:
        """Filter pod analyses by namespace."""
        if namespace == 'all':
            return analyses
        return [analysis for analysis in analyses if analysis['namespace'] == namespace]


if __name__ == "__main__":
    # Test the metrics analyzer
    from mock_data import generate_mock_cluster_data
    
    pods, summary = generate_mock_cluster_data()
    analyzer = MetricsAnalyzer()
    cluster_analysis = analyzer.analyze_cluster_metrics(pods)
    
    print(f"Cluster Analysis Results:")
    print(f"Total pods: {cluster_analysis['total_pods']}")
    print(f"Overall efficiency: {cluster_analysis['efficiency_metrics']['overall_efficiency']}%")
    print(f"Potential monthly savings: ${cluster_analysis['potential_savings']['monthly_cost_savings']}")
    print(f"Severity distribution: {cluster_analysis['severity_distribution']}")
