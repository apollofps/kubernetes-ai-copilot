"""
Recommendations processing module for Kubernetes AI Copilot.
Handles recommendation aggregation, prioritization, and formatting.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class RecommendationsProcessor:
    def __init__(self):
        """Initialize the recommendations processor."""
        self.priority_weights = {
            'critical': 4,
            'warning': 3,
            'info': 2,
            'healthy': 1
        }
    
    def process_recommendations(self, cluster_analysis: Dict[str, Any], 
                              llm_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Process and aggregate all recommendations for the cluster."""
        processed = {
            'cluster_summary': self._generate_cluster_summary(cluster_analysis),
            'recommendation_categories': self._categorize_recommendations(cluster_analysis),
            'priority_matrix': self._create_priority_matrix(cluster_analysis, llm_recommendations),
            'implementation_roadmap': self._create_implementation_roadmap(cluster_analysis, llm_recommendations),
            'risk_assessment': self._assess_implementation_risks(cluster_analysis, llm_recommendations),
            'cost_benefit_analysis': self._analyze_cost_benefits(cluster_analysis, llm_recommendations)
        }
        
        return processed
    
    def _generate_cluster_summary(self, cluster_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive cluster summary."""
        total_pods = cluster_analysis['total_pods']
        severity_dist = cluster_analysis['severity_distribution']
        efficiency = cluster_analysis['efficiency_metrics']
        savings = cluster_analysis['potential_savings']
        
        # Calculate health score
        health_score = self._calculate_cluster_health_score(severity_dist, efficiency)
        
        # Determine cluster status
        if health_score >= 80:
            status = "Excellent"
            status_color = "green"
        elif health_score >= 60:
            status = "Good"
            status_color = "blue"
        elif health_score >= 40:
            status = "Fair"
            status_color = "orange"
        else:
            status = "Poor"
            status_color = "red"
        
        return {
            'total_pods': total_pods,
            'health_score': health_score,
            'status': status,
            'status_color': status_color,
            'efficiency_metrics': efficiency,
            'potential_savings': savings,
            'severity_distribution': severity_dist,
            'top_issues': self._identify_top_issues(cluster_analysis),
            'optimization_potential': self._calculate_optimization_potential(efficiency, savings)
        }
    
    def _calculate_cluster_health_score(self, severity_dist: Dict[str, int], 
                                      efficiency: Dict[str, float]) -> float:
        """Calculate overall cluster health score (0-100)."""
        total_pods = sum(severity_dist.values())
        if total_pods == 0:
            return 0.0
        
        # Weight severity distribution
        weighted_score = (
            severity_dist['healthy'] * 100 +
            severity_dist['info'] * 75 +
            severity_dist['warning'] * 50 +
            severity_dist['critical'] * 25
        ) / total_pods
        
        # Factor in efficiency
        efficiency_factor = efficiency['overall_efficiency'] / 100
        
        # Combine scores
        health_score = (weighted_score * 0.6) + (efficiency_factor * 100 * 0.4)
        
        return round(health_score, 2)
    
    def _identify_top_issues(self, cluster_analysis: Dict[str, Any]) -> List[str]:
        """Identify the most common issues across the cluster."""
        issue_counts = {}
        
        for analysis in cluster_analysis['detailed_analyses']:
            for issue in analysis['issues']:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue[0].replace('-', ' ').title() for issue, count in sorted_issues[:5]]
    
    def _calculate_optimization_potential(self, efficiency: Dict[str, float], 
                                        savings: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the potential for optimization."""
        current_efficiency = efficiency['overall_efficiency']
        
        # Estimate potential efficiency improvement
        if current_efficiency < 50:
            potential_improvement = 30
        elif current_efficiency < 70:
            potential_improvement = 20
        elif current_efficiency < 85:
            potential_improvement = 10
        else:
            potential_improvement = 5
        
        # Calculate potential cost savings
        current_monthly_cost = savings['monthly_cost_savings']
        potential_cost_savings = current_monthly_cost * (potential_improvement / 100)
        
        return {
            'current_efficiency': current_efficiency,
            'potential_improvement': potential_improvement,
            'target_efficiency': min(95, current_efficiency + potential_improvement),
            'current_monthly_savings': current_monthly_cost,
            'potential_additional_savings': potential_cost_savings,
            'total_potential_savings': current_monthly_cost + potential_cost_savings
        }
    
    def _categorize_recommendations(self, cluster_analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize recommendations by type and impact."""
        categories = {
            'resource_optimization': [],
            'cost_reduction': [],
            'stability_improvement': [],
            'performance_enhancement': []
        }
        
        for analysis in cluster_analysis['detailed_analyses']:
            pod_name = analysis['pod_name']
            namespace = analysis['namespace']
            severity = analysis['severity']
            savings = analysis['potential_savings']
            
            # Categorize based on issues and recommendations
            if 'over-provisioned' in analysis['issues'] or 'resource-waste' in analysis['issues']:
                categories['resource_optimization'].append({
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'severity': severity,
                    'monthly_savings': savings['monthly_cost_savings'],
                    'description': 'Optimize over-provisioned resources'
                })
            
            if savings['monthly_cost_savings'] > 5:  # Significant cost savings
                categories['cost_reduction'].append({
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'severity': severity,
                    'monthly_savings': savings['monthly_cost_savings'],
                    'description': 'Reduce resource costs'
                })
            
            if 'frequent-restarts' in analysis['issues'] or 'high-restarts' in analysis['issues']:
                categories['stability_improvement'].append({
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'severity': severity,
                    'monthly_savings': savings['monthly_cost_savings'],
                    'description': 'Improve pod stability'
                })
            
            if 'high-cpu-pressure' in analysis['issues'] or 'high-memory-pressure' in analysis['issues']:
                categories['performance_enhancement'].append({
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'severity': severity,
                    'monthly_savings': savings['monthly_cost_savings'],
                    'description': 'Enhance performance'
                })
        
        return categories
    
    def _create_priority_matrix(self, cluster_analysis: Dict[str, Any], 
                              llm_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a priority matrix for implementation."""
        priority_matrix = []
        
        for analysis in cluster_analysis['detailed_analyses']:
            pod_name = analysis['pod_name']
            namespace = analysis['namespace']
            severity = analysis['severity']
            savings = analysis['potential_savings']
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(severity, savings, analysis['issues'])
            
            # Get LLM recommendation if available
            llm_rec = llm_recommendations.get(f"{namespace}/{pod_name}")
            ai_priority = llm_rec.get('priority', 'medium') if llm_rec else 'medium'
            
            priority_matrix.append({
                'pod_name': pod_name,
                'namespace': namespace,
                'severity': severity,
                'ai_priority': ai_priority,
                'priority_score': priority_score,
                'monthly_savings': savings['monthly_cost_savings'],
                'issues_count': len(analysis['issues']),
                'implementation_effort': self._estimate_implementation_effort(analysis),
                'risk_level': self._assess_implementation_risk(analysis)
            })
        
        # Sort by priority score
        priority_matrix.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_matrix
    
    def _calculate_priority_score(self, severity: str, savings: Dict[str, Any], 
                                issues: List[str]) -> float:
        """Calculate priority score for a pod."""
        severity_weight = self.priority_weights.get(severity, 1)
        cost_weight = min(savings['monthly_cost_savings'] / 10, 5)  # Cap at 5
        issues_weight = min(len(issues), 5)  # Cap at 5
        
        priority_score = (severity_weight * 2) + cost_weight + issues_weight
        
        return round(priority_score, 2)
    
    def _estimate_implementation_effort(self, analysis: Dict[str, Any]) -> str:
        """Estimate implementation effort for a pod."""
        issues_count = len(analysis['issues'])
        savings = analysis['potential_savings']['monthly_cost_savings']
        
        if issues_count <= 2 and savings < 5:
            return "Low"
        elif issues_count <= 4 and savings < 20:
            return "Medium"
        else:
            return "High"
    
    def _assess_implementation_risk(self, analysis: Dict[str, Any]) -> str:
        """Assess implementation risk for a pod."""
        severity = analysis['severity']
        issues = analysis['issues']
        
        if severity == 'critical' or 'high-cpu-pressure' in issues or 'high-memory-pressure' in issues:
            return "High"
        elif severity == 'warning' or 'frequent-restarts' in issues:
            return "Medium"
        else:
            return "Low"
    
    def _create_implementation_roadmap(self, cluster_analysis: Dict[str, Any], 
                                     llm_recommendations: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Create an implementation roadmap with phases."""
        priority_matrix = self._create_priority_matrix(cluster_analysis, llm_recommendations)
        
        roadmap = {
            'phase_1_quick_wins': [],
            'phase_2_medium_impact': [],
            'phase_3_complex_optimizations': []
        }
        
        for item in priority_matrix:
            if item['implementation_effort'] == 'Low' and item['risk_level'] == 'Low':
                roadmap['phase_1_quick_wins'].append(item)
            elif item['implementation_effort'] == 'Medium' or item['risk_level'] == 'Medium':
                roadmap['phase_2_medium_impact'].append(item)
            else:
                roadmap['phase_3_complex_optimizations'].append(item)
        
        return roadmap
    
    def _assess_implementation_risks(self, cluster_analysis: Dict[str, Any], 
                                   llm_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall implementation risks."""
        total_pods = cluster_analysis['total_pods']
        high_risk_pods = 0
        medium_risk_pods = 0
        low_risk_pods = 0
        
        for analysis in cluster_analysis['detailed_analyses']:
            risk_level = self._assess_implementation_risk(analysis)
            if risk_level == 'High':
                high_risk_pods += 1
            elif risk_level == 'Medium':
                medium_risk_pods += 1
            else:
                low_risk_pods += 1
        
        return {
            'total_pods': total_pods,
            'high_risk_pods': high_risk_pods,
            'medium_risk_pods': medium_risk_pods,
            'low_risk_pods': low_risk_pods,
            'risk_distribution': {
                'high': round((high_risk_pods / total_pods) * 100, 1),
                'medium': round((medium_risk_pods / total_pods) * 100, 1),
                'low': round((low_risk_pods / total_pods) * 100, 1)
            },
            'recommended_approach': self._recommend_implementation_approach(high_risk_pods, medium_risk_pods, low_risk_pods)
        }
    
    def _recommend_implementation_approach(self, high_risk: int, medium_risk: int, low_risk: int) -> str:
        """Recommend implementation approach based on risk distribution."""
        total = high_risk + medium_risk + low_risk
        if total == 0:
            return "No implementation needed"
        
        high_risk_percentage = (high_risk / total) * 100
        
        if high_risk_percentage > 30:
            return "Gradual rollout with extensive testing recommended"
        elif high_risk_percentage > 15:
            return "Phased implementation with monitoring"
        else:
            return "Standard implementation approach suitable"
    
    def _analyze_cost_benefits(self, cluster_analysis: Dict[str, Any], 
                             llm_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost-benefit of implementing recommendations."""
        total_savings = cluster_analysis['potential_savings']['monthly_cost_savings']
        total_pods = cluster_analysis['total_pods']
        
        # Estimate implementation costs (time and resources)
        implementation_hours = total_pods * 0.5  # 30 minutes per pod on average
        implementation_cost = implementation_hours * 100  # $100/hour for engineer time
        
        # Calculate ROI
        monthly_roi = (total_savings / implementation_cost) * 100 if implementation_cost > 0 else 0
        annual_roi = monthly_roi * 12
        
        # Payback period
        payback_period_months = implementation_cost / total_savings if total_savings > 0 else float('inf')
        
        return {
            'implementation_cost': round(implementation_cost, 2),
            'monthly_savings': round(total_savings, 2),
            'annual_savings': round(total_savings * 12, 2),
            'monthly_roi': round(monthly_roi, 2),
            'annual_roi': round(annual_roi, 2),
            'payback_period_months': round(payback_period_months, 1),
            'net_benefit_12_months': round((total_savings * 12) - implementation_cost, 2)
        }


if __name__ == "__main__":
    # Test the recommendations processor
    from mock_data import generate_mock_cluster_data
    from metrics_analyzer import MetricsAnalyzer
    
    # Generate test data
    pods, summary = generate_mock_cluster_data()
    analyzer = MetricsAnalyzer()
    cluster_analysis = analyzer.analyze_cluster_metrics(pods)
    
    # Process recommendations
    processor = RecommendationsProcessor()
    processed = processor.process_recommendations(cluster_analysis, {})
    
    print("=== CLUSTER SUMMARY ===")
    summary = processed['cluster_summary']
    print(f"Health Score: {summary['health_score']}")
    print(f"Status: {summary['status']}")
    print(f"Top Issues: {summary['top_issues']}")
    
    print("\n=== COST-BENEFIT ANALYSIS ===")
    cost_benefit = processed['cost_benefit_analysis']
    print(f"Implementation Cost: ${cost_benefit['implementation_cost']}")
    print(f"Monthly Savings: ${cost_benefit['monthly_savings']}")
    print(f"Annual ROI: {cost_benefit['annual_roi']}%")
    print(f"Payback Period: {cost_benefit['payback_period_months']} months")
