#!/usr/bin/env python3
"""
Demo script for Kubernetes AI Copilot POC
Shows key features and capabilities without requiring API keys.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mock_data import generate_mock_cluster_data
from src.metrics_analyzer import MetricsAnalyzer
from src.llm_client import LLMClient
from src.yaml_generator import YAMLGenerator
from src.recommendations import RecommendationsProcessor


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n📊 {title}")
    print("-" * 40)


def demo_mock_data():
    """Demonstrate mock data generation."""
    print_header("MOCK DATA GENERATION")
    
    pods, summary = generate_mock_cluster_data()
    
    print(f"✅ Generated {len(pods)} pods across {len(summary['namespaces'])} namespaces")
    print(f"📈 Overall cluster efficiency: {summary['overall_efficiency']:.1f}%")
    print(f"💰 Total CPU Request: {summary['total_cpu_request']}m")
    print(f"💰 Total Memory Request: {summary['total_memory_request']}Mi")
    
    print_section("Sample Pod Data")
    sample_pod = pods[0]
    print(f"Pod: {sample_pod['name']}")
    print(f"Namespace: {sample_pod['namespace']}")
    print(f"CPU Request: {sample_pod['resources']['cpu_request']}m")
    print(f"CPU Usage: {sample_pod['resources']['cpu_usage']}m")
    print(f"CPU Efficiency: {sample_pod['efficiency']['cpu_efficiency']:.1f}%")
    print(f"Issues: {', '.join(sample_pod['issues'])}")
    
    return pods, summary


def demo_metrics_analysis(pods):
    """Demonstrate metrics analysis."""
    print_header("METRICS ANALYSIS")
    
    analyzer = MetricsAnalyzer()
    cluster_analysis = analyzer.analyze_cluster_metrics(pods)
    
    print(f"🔍 Analyzed {cluster_analysis['total_pods']} pods")
    print(f"📊 Severity distribution:")
    for severity, count in cluster_analysis['severity_distribution'].items():
        print(f"   {severity.title()}: {count} pods")
    
    print_section("Top Optimization Opportunities")
    for i, opp in enumerate(cluster_analysis['top_optimization_opportunities'][:3], 1):
        print(f"{i}. {opp['pod_name']} ({opp['namespace']}) - ${opp['monthly_savings']:.2f}/month")
    
    return cluster_analysis


def demo_llm_recommendations(pods, cluster_analysis):
    """Demonstrate LLM recommendations (fallback mode)."""
    print_header("AI-POWERED RECOMMENDATIONS")
    
    # Test with fallback mode (no API keys required)
    try:
        # Use the metrics analyzer to get recommendations directly
        from src.metrics_analyzer import MetricsAnalyzer
        analyzer = MetricsAnalyzer()
        sample_pod = pods[0]
        sample_analysis = analyzer.analyze_pod_metrics(sample_pod)
        
        print(f"🤖 Recommendation for {sample_pod['name']}:")
        print(f"   Severity: {sample_analysis['severity']}")
        print(f"   Issues: {', '.join(sample_analysis['issues'])}")
        print(f"   Monthly Savings: ${sample_analysis['potential_savings']['monthly_cost_savings']:.2f}")
        
        if sample_analysis.get('recommendations'):
            print_section("Specific Recommendations")
            for i, rec in enumerate(sample_analysis['recommendations'][:2], 1):
                print(f"{i}. {rec['type'].replace('_', ' ').title()}")
                print(f"   Current: {rec['current']} → Recommended: {rec['recommended']}")
                print(f"   Reasoning: {rec['reason']}")
        
        print("\n💡 Note: For AI-powered recommendations, install OpenAI/Anthropic packages and configure API keys")
        
    except Exception as e:
        print(f"⚠️ Recommendation analysis failed: {e}")
        print("   (This is expected without proper setup)")


def demo_yaml_generation(pods, cluster_analysis):
    """Demonstrate YAML generation."""
    print_header("YAML GENERATION")
    
    yaml_gen = YAMLGenerator()
    sample_pod = pods[0]
    sample_analysis = cluster_analysis['detailed_analyses'][0]
    
    print(f"📝 Generating YAML for {sample_pod['name']}")
    
    # Generate different YAML formats
    current_yaml = yaml_gen.generate_current_manifest(sample_pod)
    optimized_yaml = yaml_gen.generate_optimized_manifest(sample_pod, sample_analysis['recommendations'])
    patch_yaml = yaml_gen.generate_patch_manifest(sample_pod, sample_analysis['recommendations'])
    kubectl_command = yaml_gen.generate_kubectl_patch_command(sample_pod, sample_analysis['recommendations'])
    
    print_section("Current vs Optimized Resources")
    print("Current CPU Request:", sample_pod['resources']['cpu_request'], "m")
    print("Current Memory Request:", sample_pod['resources']['memory_request'], "Mi")
    
    if sample_analysis['recommendations']:
        for rec in sample_analysis['recommendations']:
            if rec['type'] == 'cpu_request':
                print(f"Recommended CPU Request: {rec['recommended']}m")
            elif rec['type'] == 'memory_request':
                print(f"Recommended Memory Request: {rec['recommended']}Mi")
    
    print_section("kubectl Patch Command")
    print(kubectl_command)
    
    # Generate comparison summary
    comparison = yaml_gen.generate_comparison_summary(sample_pod, sample_analysis['recommendations'])
    print_section("Change Summary")
    print(f"Total changes: {comparison['total_changes']}")
    print(f"CPU savings: {comparison['total_cpu_savings']} millicores")
    print(f"Memory savings: {comparison['total_memory_savings']} MB")


def demo_recommendations_processing(cluster_analysis):
    """Demonstrate recommendations processing."""
    print_header("RECOMMENDATIONS PROCESSING")
    
    processor = RecommendationsProcessor()
    processed = processor.process_recommendations(cluster_analysis, {})
    
    # Cluster summary
    summary = processed['cluster_summary']
    print(f"🏥 Cluster Health Score: {summary['health_score']}/100")
    print(f"📊 Status: {summary['status']}")
    print(f"🎯 Top Issues: {', '.join(summary['top_issues'][:3])}")
    
    # Cost-benefit analysis
    cost_benefit = processed['cost_benefit_analysis']
    print_section("Cost-Benefit Analysis")
    print(f"Implementation Cost: ${cost_benefit['implementation_cost']}")
    print(f"Monthly Savings: ${cost_benefit['monthly_savings']}")
    print(f"Annual ROI: {cost_benefit['annual_roi']}%")
    print(f"Payback Period: {cost_benefit['payback_period_months']} months")
    
    # Implementation roadmap
    roadmap = processed['implementation_roadmap']
    print_section("Implementation Roadmap")
    print(f"Phase 1 (Quick Wins): {len(roadmap['phase_1_quick_wins'])} pods")
    print(f"Phase 2 (Medium Impact): {len(roadmap['phase_2_medium_impact'])} pods")
    print(f"Phase 3 (Complex): {len(roadmap['phase_3_complex_optimizations'])} pods")


def main():
    """Run the complete demo."""
    print_header("KUBERNETES AI COPILOT POC DEMO")
    print("This demo showcases the key features of the Kubernetes AI Copilot")
    print("without requiring API keys or a real Kubernetes cluster.")
    
    try:
        # 1. Mock Data Generation
        pods, summary = demo_mock_data()
        
        # 2. Metrics Analysis
        cluster_analysis = demo_metrics_analysis(pods)
        
        # 3. LLM Recommendations
        demo_llm_recommendations(pods, cluster_analysis)
        
        # 4. YAML Generation
        demo_yaml_generation(pods, cluster_analysis)
        
        # 5. Recommendations Processing
        demo_recommendations_processing(cluster_analysis)
        
        print_header("DEMO COMPLETED SUCCESSFULLY! 🎉")
        print("To run the full interactive dashboard:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure API keys in .env file (optional)")
        print("3. Run: streamlit run app.py")
        print("4. Open http://localhost:8501 in your browser")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
