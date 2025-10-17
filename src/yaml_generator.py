"""
YAML generator for Kubernetes resource optimization.
Generates before/after YAML configurations and patches.
"""

import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime


class YAMLGenerator:
    def __init__(self):
        """Initialize the YAML generator."""
        pass
    
    def _get_recommendation_value(self, rec: Dict[str, Any], field: str) -> Any:
        """Get a value from recommendation, handling both LLM and metrics analyzer formats."""
        if field == 'resource_type':
            return rec.get('resource_type', rec.get('type', ''))
        elif field == 'current_value':
            value = rec.get('current_value', rec.get('current', 0))
            return int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
        elif field == 'recommended_value':
            value = rec.get('recommended_value', rec.get('recommended', 0))
            return int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
        elif field == 'reasoning':
            return rec.get('reasoning', rec.get('reason', 'No reasoning provided'))
        elif field == 'impact':
            return rec.get('impact', 'No impact information')
        elif field == 'risk_level':
            return rec.get('risk_level', 'medium')
        else:
            return rec.get(field, '')
    
    def generate_current_manifest(self, pod_data: Dict[str, Any]) -> str:
        """Generate the current pod manifest in YAML format."""
        resources = pod_data['resources']
        
        manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': pod_data['name'],
                'namespace': pod_data['namespace'],
                'labels': {
                    'app': pod_data['name'],
                    'workload-type': pod_data.get('workload_type', 'unknown')
                }
            },
            'spec': {
                'containers': [
                    {
                        'name': f"{pod_data['name']}-container",
                        'image': 'nginx:latest',  # Placeholder image
                        'resources': {
                            'requests': {
                                'cpu': f"{resources['cpu_request']}m",
                                'memory': f"{resources['memory_request']}Mi"
                            },
                            'limits': {
                                'cpu': f"{resources['cpu_limit']}m",
                                'memory': f"{resources['memory_limit']}Mi"
                            }
                        }
                    }
                ],
                'restartPolicy': 'Always'
            }
        }
        
        return yaml.dump(manifest, default_flow_style=False, sort_keys=False)
    
    def generate_optimized_manifest(self, pod_data: Dict[str, Any], 
                                  recommendations: List[Dict[str, Any]]) -> str:
        """Generate the optimized pod manifest based on recommendations."""
        resources = pod_data['resources']
        
        # Apply recommendations to create optimized resources
        optimized_cpu_request = resources['cpu_request']
        optimized_memory_request = resources['memory_request']
        optimized_cpu_limit = resources['cpu_limit']
        optimized_memory_limit = resources['memory_limit']
        
        for rec in recommendations:
            resource_type = self._get_recommendation_value(rec, 'resource_type')
            recommended_value = self._get_recommendation_value(rec, 'recommended_value')
            
            if resource_type == 'cpu_request':
                optimized_cpu_request = recommended_value
            elif resource_type == 'memory_request':
                optimized_memory_request = recommended_value
            elif resource_type == 'cpu_limit':
                optimized_cpu_limit = recommended_value
            elif resource_type == 'memory_limit':
                optimized_memory_limit = recommended_value
        
        manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': pod_data['name'],
                'namespace': pod_data['namespace'],
                'labels': {
                    'app': pod_data['name'],
                    'workload-type': pod_data.get('workload_type', 'unknown'),
                    'optimized': 'true',
                    'optimized-at': datetime.now().isoformat()
                }
            },
            'spec': {
                'containers': [
                    {
                        'name': f"{pod_data['name']}-container",
                        'image': 'nginx:latest',  # Placeholder image
                        'resources': {
                            'requests': {
                                'cpu': f"{optimized_cpu_request}m",
                                'memory': f"{optimized_memory_request}Mi"
                            },
                            'limits': {
                                'cpu': f"{optimized_cpu_limit}m",
                                'memory': f"{optimized_memory_limit}Mi"
                            }
                        }
                    }
                ],
                'restartPolicy': 'Always'
            }
        }
        
        return yaml.dump(manifest, default_flow_style=False, sort_keys=False)
    
    def generate_patch_manifest(self, pod_data: Dict[str, Any], 
                              recommendations: List[Dict[str, Any]]) -> str:
        """Generate a strategic merge patch for the pod."""
        patch = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': pod_data['name'],
                'namespace': pod_data['namespace']
            },
            'spec': {
                'containers': [
                    {
                        'name': f"{pod_data['name']}-container",
                        'resources': {
                            'requests': {},
                            'limits': {}
                        }
                    }
                ]
            }
        }
        
        # Add only the changed resources to the patch
        for rec in recommendations:
            resource_type = self._get_recommendation_value(rec, 'resource_type')
            recommended_value = self._get_recommendation_value(rec, 'recommended_value')
            
            if resource_type == 'cpu_request':
                patch['spec']['containers'][0]['resources']['requests']['cpu'] = f"{recommended_value}m"
            elif resource_type == 'memory_request':
                patch['spec']['containers'][0]['resources']['requests']['memory'] = f"{recommended_value}Mi"
            elif resource_type == 'cpu_limit':
                patch['spec']['containers'][0]['resources']['limits']['cpu'] = f"{recommended_value}m"
            elif resource_type == 'memory_limit':
                patch['spec']['containers'][0]['resources']['limits']['memory'] = f"{recommended_value}Mi"
        
        return yaml.dump(patch, default_flow_style=False, sort_keys=False)
    
    def generate_kubectl_patch_command(self, pod_data: Dict[str, Any], 
                                     recommendations: List[Dict[str, Any]]) -> str:
        """Generate kubectl patch command for applying the changes."""
        patch_data = {}
        
        for rec in recommendations:
            resource_type = self._get_recommendation_value(rec, 'resource_type')
            recommended_value = self._get_recommendation_value(rec, 'recommended_value')
            
            if resource_type == 'cpu_request':
                patch_data['spec.containers[0].resources.requests.cpu'] = f"{recommended_value}m"
            elif resource_type == 'memory_request':
                patch_data['spec.containers[0].resources.requests.memory'] = f"{recommended_value}Mi"
            elif resource_type == 'cpu_limit':
                patch_data['spec.containers[0].resources.limits.cpu'] = f"{recommended_value}m"
            elif resource_type == 'memory_limit':
                patch_data['spec.containers[0].resources.limits.memory'] = f"{recommended_value}Mi"
        
        # Build the kubectl patch command
        patch_pairs = []
        for key, value in patch_data.items():
            patch_pairs.append(f'"{key}":"{value}"')
        
        patch_json = "{" + ",".join(patch_pairs) + "}"
        
        command = f"""kubectl patch pod {pod_data['name']} -n {pod_data['namespace']} --type='merge' -p='{patch_json}'"""
        
        return command
    
    def generate_deployment_manifest(self, pod_data: Dict[str, Any], 
                                   recommendations: List[Dict[str, Any]]) -> str:
        """Generate a Deployment manifest with optimized resources."""
        resources = pod_data['resources']
        
        # Apply recommendations
        optimized_cpu_request = resources['cpu_request']
        optimized_memory_request = resources['memory_request']
        optimized_cpu_limit = resources['cpu_limit']
        optimized_memory_limit = resources['memory_limit']
        
        for rec in recommendations:
            resource_type = self._get_recommendation_value(rec, 'resource_type')
            recommended_value = self._get_recommendation_value(rec, 'recommended_value')
            
            if resource_type == 'cpu_request':
                optimized_cpu_request = recommended_value
            elif resource_type == 'memory_request':
                optimized_memory_request = recommended_value
            elif resource_type == 'cpu_limit':
                optimized_cpu_limit = recommended_value
            elif resource_type == 'memory_limit':
                optimized_memory_limit = recommended_value
        
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': f"{pod_data['name']}-deployment",
                'namespace': pod_data['namespace'],
                'labels': {
                    'app': pod_data['name'],
                    'workload-type': pod_data.get('workload_type', 'unknown'),
                    'optimized': 'true'
                }
            },
            'spec': {
                'replicas': 1,
                'selector': {
                    'matchLabels': {
                        'app': pod_data['name']
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': pod_data['name']
                        }
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': f"{pod_data['name']}-container",
                                'image': 'nginx:latest',
                                'resources': {
                                    'requests': {
                                        'cpu': f"{optimized_cpu_request}m",
                                        'memory': f"{optimized_memory_request}Mi"
                                    },
                                    'limits': {
                                        'cpu': f"{optimized_cpu_limit}m",
                                        'memory': f"{optimized_memory_limit}Mi"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        return yaml.dump(deployment, default_flow_style=False, sort_keys=False)
    
    def generate_comparison_summary(self, pod_data: Dict[str, Any], 
                                  recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of changes for comparison."""
        changes = []
        
        for rec in recommendations:
            resource_type = self._get_recommendation_value(rec, 'resource_type')
            current_value = self._get_recommendation_value(rec, 'current_value')
            recommended_value = self._get_recommendation_value(rec, 'recommended_value')
            
            change = {
                'resource_type': resource_type,
                'current_value': current_value,
                'recommended_value': recommended_value,
                'change_percentage': self._calculate_change_percentage(
                    current_value, recommended_value
                ),
                'reasoning': self._get_recommendation_value(rec, 'reasoning'),
                'impact': self._get_recommendation_value(rec, 'impact'),
                'risk_level': self._get_recommendation_value(rec, 'risk_level')
            }
            changes.append(change)
        
        # Calculate total savings
        total_cpu_savings = sum(
            change['current_value'] - change['recommended_value'] 
            for change in changes 
            if change['resource_type'] in ['cpu_request', 'cpu_limit']
        )
        
        total_memory_savings = sum(
            change['current_value'] - change['recommended_value'] 
            for change in changes 
            if change['resource_type'] in ['memory_request', 'memory_limit']
        )
        
        return {
            'pod_name': pod_data['name'],
            'namespace': pod_data['namespace'],
            'changes': changes,
            'total_cpu_savings': max(0, total_cpu_savings),
            'total_memory_savings': max(0, total_memory_savings),
            'total_changes': len(changes),
            'high_risk_changes': len([c for c in changes if c['risk_level'] == 'high']),
            'medium_risk_changes': len([c for c in changes if c['risk_level'] == 'medium']),
            'low_risk_changes': len([c for c in changes if c['risk_level'] == 'low'])
        }
    
    def _calculate_change_percentage(self, current: int, recommended: int) -> float:
        """Calculate the percentage change between current and recommended values."""
        if current == 0:
            return 0.0
        return round(((recommended - current) / current) * 100, 2)
    
    def generate_export_package(self, pod_data: Dict[str, Any], 
                              recommendations: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate a complete export package with all YAML files."""
        return {
            'current_manifest.yaml': self.generate_current_manifest(pod_data),
            'optimized_manifest.yaml': self.generate_optimized_manifest(pod_data, recommendations),
            'patch_manifest.yaml': self.generate_patch_manifest(pod_data, recommendations),
            'deployment_manifest.yaml': self.generate_deployment_manifest(pod_data, recommendations),
            'kubectl_patch_command.txt': self.generate_kubectl_patch_command(pod_data, recommendations),
            'comparison_summary.json': str(self.generate_comparison_summary(pod_data, recommendations))
        }


if __name__ == "__main__":
    # Test the YAML generator
    from mock_data import generate_mock_cluster_data
    from metrics_analyzer import MetricsAnalyzer
    
    # Generate test data
    pods, summary = generate_mock_cluster_data()
    analyzer = MetricsAnalyzer()
    
    # Test with a sample pod
    test_pod = pods[0]
    test_analysis = analyzer.analyze_pod_metrics(test_pod)
    
    # Generate YAML files
    yaml_gen = YAMLGenerator()
    
    print("=== CURRENT MANIFEST ===")
    print(yaml_gen.generate_current_manifest(test_pod))
    
    print("\n=== OPTIMIZED MANIFEST ===")
    print(yaml_gen.generate_optimized_manifest(test_pod, test_analysis['recommendations']))
    
    print("\n=== PATCH MANIFEST ===")
    print(yaml_gen.generate_patch_manifest(test_pod, test_analysis['recommendations']))
    
    print("\n=== KUBECTL PATCH COMMAND ===")
    print(yaml_gen.generate_kubectl_patch_command(test_pod, test_analysis['recommendations']))
    
    print("\n=== COMPARISON SUMMARY ===")
    summary = yaml_gen.generate_comparison_summary(test_pod, test_analysis['recommendations'])
    print(f"Pod: {summary['pod_name']}")
    print(f"Total changes: {summary['total_changes']}")
    print(f"CPU savings: {summary['total_cpu_savings']} millicores")
    print(f"Memory savings: {summary['total_memory_savings']} MB")