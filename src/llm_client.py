"""
LLM client for Kubernetes resource optimization recommendations.
Supports both OpenAI GPT-4 and Anthropic Claude APIs.
"""

import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Conditional imports for optional dependencies
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Load environment variables
load_dotenv()


class LLMClient:
    def __init__(self, provider: str = "openai"):
        """Initialize the LLM client with the specified provider."""
        self.provider = provider.lower()
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize the appropriate LLM client based on provider."""
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ValueError("OpenAI package not installed. Install with: pip install openai")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4"
        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ValueError("Anthropic package not installed. Install with: pip install anthropic")
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-3-sonnet-20240229"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def get_resource_recommendation(self, pod_data: Dict[str, Any], 
                                  analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered resource optimization recommendations for a pod."""
        prompt = self._build_recommendation_prompt(pod_data, analysis)
        
        try:
            if self.provider == "openai":
                response = self._get_openai_response(prompt)
            else:
                response = self._get_anthropic_response(prompt)
            
            return self._parse_recommendation_response(response, pod_data, analysis)
            
        except Exception as e:
            return self._get_fallback_recommendation(pod_data, analysis, str(e))
    
    def _build_recommendation_prompt(self, pod_data: Dict[str, Any], 
                                   analysis: Dict[str, Any]) -> str:
        """Build a structured prompt for resource optimization recommendations."""
        resources = pod_data['resources']
        efficiency = pod_data['efficiency']
        issues = pod_data['issues']
        restart_count = pod_data['restart_count']
        
        prompt = f"""
You are a Kubernetes resource optimization expert. Analyze the following pod metrics and provide specific, actionable recommendations for resource optimization.

POD INFORMATION:
- Name: {pod_data['name']}
- Namespace: {pod_data['namespace']}
- Workload Type: {pod_data.get('workload_type', 'unknown')}

CURRENT RESOURCE SPECIFICATIONS:
- CPU Request: {resources['cpu_request']} millicores
- CPU Limit: {resources['cpu_limit']} millicores
- Memory Request: {resources['memory_request']} MB
- Memory Limit: {resources['memory_limit']} MB

CURRENT USAGE:
- CPU Usage: {resources['cpu_usage']} millicores ({efficiency['cpu_efficiency']:.1f}% of request)
- Memory Usage: {resources['memory_usage']} MB ({efficiency['memory_efficiency']:.1f}% of request)

ISSUES IDENTIFIED:
{', '.join(issues) if issues else 'No specific issues detected'}

RESTART COUNT: {restart_count}

POTENTIAL SAVINGS:
- CPU Savings: {analysis['potential_savings']['cpu_savings_millicores']} millicores
- Memory Savings: {analysis['potential_savings']['memory_savings_mb']} MB
- Monthly Cost Savings: ${analysis['potential_savings']['monthly_cost_savings']}

Please provide:
1. A brief summary of the current resource utilization
2. Specific recommendations for CPU and memory optimization
3. The reasoning behind each recommendation
4. Potential risks and mitigation strategies
5. Expected impact on performance and cost

Format your response as a JSON object with the following structure:
{{
    "summary": "Brief summary of current state",
    "recommendations": [
        {{
            "resource_type": "cpu_request|cpu_limit|memory_request|memory_limit",
            "current_value": current_value,
            "recommended_value": recommended_value,
            "reasoning": "Explanation for the recommendation",
            "impact": "Expected impact on performance/cost",
            "risk_level": "low|medium|high"
        }}
    ],
    "overall_assessment": "Overall assessment of the pod's resource configuration",
    "priority": "high|medium|low",
    "estimated_savings": {{
        "cpu_millicores": estimated_cpu_savings,
        "memory_mb": estimated_memory_savings,
        "monthly_cost_usd": estimated_monthly_savings
    }}
}}
"""
        return prompt
    
    def _get_openai_response(self, prompt: str) -> str:
        """Get response from OpenAI GPT-4."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Kubernetes resource optimization expert. Provide detailed, actionable recommendations in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content
    
    def _get_anthropic_response(self, prompt: str) -> str:
        """Get response from Anthropic Claude."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _parse_recommendation_response(self, response: str, pod_data: Dict[str, Any], 
                                     analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the LLM response and extract structured recommendations."""
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                parsed_response = json.loads(json_str)
                
                # Validate and enhance the response
                return self._validate_and_enhance_response(parsed_response, pod_data, analysis)
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            return self._get_fallback_recommendation(pod_data, analysis, f"Failed to parse LLM response: {str(e)}")
    
    def _validate_and_enhance_response(self, parsed_response: Dict[str, Any], 
                                     pod_data: Dict[str, Any], 
                                     analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the parsed LLM response."""
        # Ensure required fields exist
        if 'recommendations' not in parsed_response:
            parsed_response['recommendations'] = []
        
        if 'summary' not in parsed_response:
            parsed_response['summary'] = "Resource optimization analysis completed"
        
        if 'overall_assessment' not in parsed_response:
            parsed_response['overall_assessment'] = "Pod requires resource optimization"
        
        if 'priority' not in parsed_response:
            parsed_response['priority'] = analysis['severity']
        
        # Add metadata
        parsed_response['llm_provider'] = self.provider
        parsed_response['model'] = self.model
        parsed_response['pod_name'] = pod_data['name']
        parsed_response['namespace'] = pod_data['namespace']
        
        return parsed_response
    
    def _get_fallback_recommendation(self, pod_data: Dict[str, Any], 
                                   analysis: Dict[str, Any], 
                                   error_message: str) -> Dict[str, Any]:
        """Generate a fallback recommendation when LLM fails."""
        resources = pod_data['resources']
        recommendations = []
        
        # Generate basic recommendations based on analysis
        for rec in analysis['recommendations']:
            recommendations.append({
                "resource_type": rec['type'],
                "current_value": rec['current'],
                "recommended_value": rec['recommended'],
                "reasoning": rec['reason'],
                "impact": rec['impact'],
                "risk_level": "medium"
            })
        
        return {
            "summary": f"Fallback analysis for {pod_data['name']} (LLM unavailable: {error_message})",
            "recommendations": recommendations,
            "overall_assessment": "Pod requires resource optimization based on metrics analysis",
            "priority": analysis['severity'],
            "estimated_savings": analysis['potential_savings'],
            "llm_provider": "fallback",
            "model": "rule-based",
            "pod_name": pod_data['name'],
            "namespace": pod_data['namespace'],
            "error": error_message
        }
    
    def get_cluster_insights(self, cluster_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered insights for cluster-wide optimization."""
        prompt = self._build_cluster_insights_prompt(cluster_analysis)
        
        try:
            if self.provider == "openai":
                response = self._get_openai_response(prompt)
            else:
                response = self._get_anthropic_response(prompt)
            
            return self._parse_cluster_insights_response(response, cluster_analysis)
            
        except Exception as e:
            return self._get_fallback_cluster_insights(cluster_analysis, str(e))
    
    def _build_cluster_insights_prompt(self, cluster_analysis: Dict[str, Any]) -> str:
        """Build a prompt for cluster-wide optimization insights."""
        total_pods = cluster_analysis['total_pods']
        severity_dist = cluster_analysis['severity_distribution']
        efficiency = cluster_analysis['efficiency_metrics']
        savings = cluster_analysis['potential_savings']
        top_opportunities = cluster_analysis['top_optimization_opportunities']
        
        prompt = f"""
You are a Kubernetes cluster optimization expert. Analyze the following cluster metrics and provide strategic insights for resource optimization.

CLUSTER OVERVIEW:
- Total Pods: {total_pods}
- Overall CPU Efficiency: {efficiency['cpu_efficiency']:.1f}%
- Overall Memory Efficiency: {efficiency['memory_efficiency']:.1f}%
- Overall Efficiency Score: {efficiency['overall_efficiency']:.1f}%

SEVERITY DISTRIBUTION:
- Critical Issues: {severity_dist['critical']} pods
- Warning Issues: {severity_dist['warning']} pods
- Info Issues: {severity_dist['info']} pods
- Healthy: {severity_dist['healthy']} pods

POTENTIAL SAVINGS:
- CPU Savings: {savings['cpu_savings_millicores']} millicores
- Memory Savings: {savings['memory_savings_mb']} MB
- Monthly Cost Savings: ${savings['monthly_cost_savings']}

TOP OPTIMIZATION OPPORTUNITIES:
{json.dumps(top_opportunities, indent=2)}

Please provide:
1. Overall cluster health assessment
2. Priority areas for optimization
3. Strategic recommendations for resource management
4. Expected impact of implementing all recommendations
5. Risk mitigation strategies

Format your response as a JSON object with the following structure:
{{
    "cluster_health": "excellent|good|fair|poor",
    "priority_areas": ["area1", "area2", "area3"],
    "strategic_recommendations": [
        {{
            "category": "resource_optimization|cost_reduction|stability_improvement",
            "recommendation": "Specific recommendation",
            "impact": "Expected impact",
            "effort": "low|medium|high"
        }}
    ],
    "expected_impact": {{
        "efficiency_improvement": "percentage improvement",
        "cost_reduction": "percentage reduction",
        "stability_improvement": "description"
    }},
    "risk_mitigation": ["strategy1", "strategy2"],
    "implementation_priority": ["recommendation1", "recommendation2"]
}}
"""
        return prompt
    
    def _parse_cluster_insights_response(self, response: str, 
                                       cluster_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse cluster insights response from LLM."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                parsed_response = json.loads(json_str)
                
                # Add metadata
                parsed_response['llm_provider'] = self.provider
                parsed_response['model'] = self.model
                parsed_response['total_pods'] = cluster_analysis['total_pods']
                
                return parsed_response
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            return self._get_fallback_cluster_insights(cluster_analysis, f"Failed to parse LLM response: {str(e)}")
    
    def _get_fallback_cluster_insights(self, cluster_analysis: Dict[str, Any], 
                                     error_message: str) -> Dict[str, Any]:
        """Generate fallback cluster insights when LLM fails."""
        efficiency = cluster_analysis['efficiency_metrics']['overall_efficiency']
        
        if efficiency > 80:
            health = "excellent"
        elif efficiency > 60:
            health = "good"
        elif efficiency > 40:
            health = "fair"
        else:
            health = "poor"
        
        return {
            "cluster_health": health,
            "priority_areas": ["Resource optimization", "Cost reduction", "Stability improvement"],
            "strategic_recommendations": [
                {
                    "category": "resource_optimization",
                    "recommendation": "Optimize over-provisioned pods",
                    "impact": "Improve cluster efficiency",
                    "effort": "medium"
                }
            ],
            "expected_impact": {
                "efficiency_improvement": "15-25%",
                "cost_reduction": "10-20%",
                "stability_improvement": "Reduced restart rates"
            },
            "risk_mitigation": ["Gradual rollout", "Monitoring", "Rollback plan"],
            "implementation_priority": ["High-impact pods first", "Test in staging"],
            "llm_provider": "fallback",
            "model": "rule-based",
            "total_pods": cluster_analysis['total_pods'],
            "error": error_message
        }


if __name__ == "__main__":
    # Test the LLM client
    from mock_data import generate_mock_cluster_data
    from metrics_analyzer import MetricsAnalyzer
    
    # Generate test data
    pods, summary = generate_mock_cluster_data()
    analyzer = MetricsAnalyzer()
    cluster_analysis = analyzer.analyze_cluster_metrics(pods)
    
    # Test with a sample pod
    test_pod = pods[0]
    test_analysis = analyzer.analyze_pod_metrics(test_pod)
    
    # Initialize LLM client (will use fallback if no API keys)
    try:
        llm_client = LLMClient("openai")
        recommendation = llm_client.get_resource_recommendation(test_pod, test_analysis)
        print(f"LLM Recommendation for {test_pod['name']}:")
        print(f"Summary: {recommendation['summary']}")
        print(f"Priority: {recommendation['priority']}")
    except Exception as e:
        print(f"LLM client test failed (expected if no API keys): {e}")
        print("Using fallback recommendations...")
