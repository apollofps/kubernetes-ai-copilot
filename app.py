"""
Kubernetes AI Copilot - Main Streamlit Application
Interactive dashboard for Kubernetes resource optimization recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
import base64
from io import StringIO

# Import our custom modules
from src.mock_data import generate_mock_cluster_data
from src.metrics_analyzer import MetricsAnalyzer
from src.llm_client import LLMClient
from src.yaml_generator import YAMLGenerator

# Page configuration
st.set_page_config(
    page_title="Kubernetes AI Copilot",
    page_icon="🕹️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .severity-critical {
        color: #d62728;
        font-weight: bold;
    }
    .severity-warning {
        color: #ff7f0e;
        font-weight: bold;
    }
    .severity-info {
        color: #2ca02c;
        font-weight: bold;
    }
    .severity-healthy {
        color: #17a2b8;
        font-weight: bold;
    }
    .yaml-diff {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cluster_data' not in st.session_state:
    st.session_state.cluster_data = None
if 'cluster_analysis' not in st.session_state:
    st.session_state.cluster_analysis = None
if 'llm_recommendations' not in st.session_state:
    st.session_state.llm_recommendations = {}
if 'selected_pod' not in st.session_state:
    st.session_state.selected_pod = None


def load_cluster_data():
    """Load and analyze cluster data."""
    with st.spinner("Generating mock cluster data..."):
        pods, summary = generate_mock_cluster_data()
        analyzer = MetricsAnalyzer()
        cluster_analysis = analyzer.analyze_cluster_metrics(pods)
        
        st.session_state.cluster_data = {
            'pods': pods,
            'summary': summary
        }
        st.session_state.cluster_analysis = cluster_analysis
        st.session_state.llm_recommendations = {}


def get_llm_recommendation(pod_data, analysis):
    """Get LLM recommendation for a pod."""
    pod_key = f"{pod_data['namespace']}/{pod_data['name']}"
    
    if pod_key not in st.session_state.llm_recommendations:
        try:
            llm_client = LLMClient(st.session_state.llm_provider)
            recommendation = llm_client.get_resource_recommendation(pod_data, analysis)
            st.session_state.llm_recommendations[pod_key] = recommendation
        except Exception as e:
            st.error(f"Failed to get LLM recommendation: {str(e)}")
            return None
    
    return st.session_state.llm_recommendations[pod_key]


def render_sidebar():
    """Render the sidebar with controls."""
    st.sidebar.title("🕹️ Kubernetes AI Copilot")
    
    # LLM Provider Selection
    st.sidebar.subheader("🤖 AI Configuration")
    llm_provider = st.sidebar.selectbox(
        "LLM Provider",
        ["openai", "anthropic"],
        index=0,
        help="Select the AI provider for recommendations"
    )
    st.session_state.llm_provider = llm_provider
    
    # Check API key availability
    if llm_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.sidebar.warning("⚠️ OpenAI API key not found. Using fallback recommendations.")
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.sidebar.warning("⚠️ Anthropic API key not found. Using fallback recommendations.")
    
    st.sidebar.divider()
    
    # Data Controls
    st.sidebar.subheader("📊 Data Controls")
    if st.sidebar.button("🔄 Refresh Cluster Data", type="primary"):
        load_cluster_data()
        st.rerun()
    
    if st.session_state.cluster_data is None:
        if st.sidebar.button("🚀 Load Initial Data"):
            load_cluster_data()
            st.rerun()
    
    # Filters
    if st.session_state.cluster_data:
        st.sidebar.subheader("🔍 Filters")
        
        # Namespace filter
        namespaces = ['all'] + list(set(pod['namespace'] for pod in st.session_state.cluster_data['pods']))
        selected_namespace = st.sidebar.selectbox("Namespace", namespaces)
        
        # Severity filter
        severities = ['all', 'critical', 'warning', 'info', 'healthy']
        selected_severity = st.sidebar.selectbox("Severity", severities)
        
        st.session_state.selected_namespace = selected_namespace
        st.session_state.selected_severity = selected_severity


def render_overview_cards():
    """Render overview metric cards."""
    if not st.session_state.cluster_analysis:
        return
    
    analysis = st.session_state.cluster_analysis
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Pods",
            value=analysis['total_pods'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Overall Efficiency",
            value=f"{analysis['efficiency_metrics']['overall_efficiency']:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Critical Issues",
            value=analysis['severity_distribution']['critical'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="Monthly Savings",
            value=f"${analysis['potential_savings']['monthly_cost_savings']:.2f}",
            delta=None
        )


def render_cluster_heatmap():
    """Render cluster resource utilization heatmap."""
    if not st.session_state.cluster_data:
        return
    
    st.subheader("🔥 Cluster Resource Utilization Heatmap")
    
    # Prepare data for heatmap
    pods = st.session_state.cluster_data['pods']
    heatmap_data = []
    
    for pod in pods:
        resources = pod['resources']
        efficiency = pod['efficiency']
        
        heatmap_data.append({
            'Pod': pod['name'],
            'Namespace': pod['namespace'],
            'CPU Efficiency': efficiency['cpu_efficiency'],
            'Memory Efficiency': efficiency['memory_efficiency'],
            'Overall Efficiency': efficiency['overall_efficiency'],
            'CPU Usage': resources['cpu_usage'],
            'Memory Usage': resources['memory_usage']
        })
    
    df = pd.DataFrame(heatmap_data)
    
    # Create heatmap
    fig = px.imshow(
        df[['CPU Efficiency', 'Memory Efficiency', 'Overall Efficiency']].T,
        labels=dict(x="Pod", y="Metric", color="Efficiency %"),
        x=df['Pod'],
        y=['CPU Efficiency', 'Memory Efficiency', 'Overall Efficiency'],
        color_continuous_scale='RdYlGn',
        aspect="auto"
    )
    
    fig.update_layout(
        title="Resource Efficiency Heatmap",
        xaxis_title="Pods",
        yaxis_title="Metrics",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_recommendations_table():
    """Render the recommendations table."""
    if not st.session_state.cluster_analysis:
        return
    
    st.subheader("📋 Optimization Recommendations")
    
    # Filter analyses based on sidebar selections
    analyses = st.session_state.cluster_analysis['detailed_analyses']
    
    if st.session_state.selected_namespace != 'all':
        analyses = [a for a in analyses if a['namespace'] == st.session_state.selected_namespace]
    
    if st.session_state.selected_severity != 'all':
        analyses = [a for a in analyses if a['severity'] == st.session_state.selected_severity]
    
    if not analyses:
        st.info("No recommendations found for the selected filters.")
        return
    
    # Create DataFrame for the table
    table_data = []
    for analysis in analyses:
        pod_data = next(p for p in st.session_state.cluster_data['pods'] 
                       if p['name'] == analysis['pod_name'])
        
        table_data.append({
            'Pod': analysis['pod_name'],
            'Namespace': analysis['namespace'],
            'Severity': analysis['severity'],
            'Issues': ', '.join(analysis['issues'][:3]),  # Show first 3 issues
            'CPU Efficiency': f"{pod_data['efficiency']['cpu_efficiency']:.1f}%",
            'Memory Efficiency': f"{pod_data['efficiency']['memory_efficiency']:.1f}%",
            'Monthly Savings': f"${analysis['potential_savings']['monthly_cost_savings']:.2f}",
            'Restart Count': pod_data['restart_count']
        })
    
    df = pd.DataFrame(table_data)
    
    # Display the table with selection
    selected_indices = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Handle row selection
    if selected_indices.selection.rows:
        selected_idx = selected_indices.selection.rows[0]
        selected_pod_name = df.iloc[selected_idx]['Pod']
        selected_namespace = df.iloc[selected_idx]['Namespace']
        
        # Find the selected pod data
        selected_pod = next(p for p in st.session_state.cluster_data['pods'] 
                           if p['name'] == selected_pod_name and p['namespace'] == selected_namespace)
        
        st.session_state.selected_pod = selected_pod
        st.rerun()


def render_detailed_analysis():
    """Render detailed analysis for selected pod."""
    if not st.session_state.selected_pod:
        st.info("👆 Select a pod from the recommendations table to view detailed analysis.")
        return
    
    pod = st.session_state.selected_pod
    analyzer = MetricsAnalyzer()
    analysis = analyzer.analyze_pod_metrics(pod)
    
    st.subheader(f"🔍 Detailed Analysis: {pod['name']}")
    
    # Get LLM recommendation
    llm_rec = get_llm_recommendation(pod, analysis)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Metrics", "🤖 AI Recommendations", "📝 YAML Comparison", "📈 Trends"])
    
    with tab1:
        render_metrics_tab(pod, analysis)
    
    with tab2:
        render_ai_recommendations_tab(pod, analysis, llm_rec)
    
    with tab3:
        render_yaml_comparison_tab(pod, analysis, llm_rec)
    
    with tab4:
        render_trends_tab(pod)


def render_metrics_tab(pod, analysis):
    """Render metrics tab."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Current Resources")
        resources = pod['resources']
        
        st.metric("CPU Request", f"{resources['cpu_request']}m")
        st.metric("CPU Limit", f"{resources['cpu_limit']}m")
        st.metric("CPU Usage", f"{resources['cpu_usage']}m")
        st.metric("CPU Efficiency", f"{pod['efficiency']['cpu_efficiency']:.1f}%")
    
    with col2:
        st.subheader("💾 Memory Resources")
        
        st.metric("Memory Request", f"{resources['memory_request']}Mi")
        st.metric("Memory Limit", f"{resources['memory_limit']}Mi")
        st.metric("Memory Usage", f"{resources['memory_usage']}Mi")
        st.metric("Memory Efficiency", f"{pod['efficiency']['memory_efficiency']:.1f}%")
    
    # Issues and risks
    st.subheader("⚠️ Issues & Risks")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Identified Issues:**")
        for issue in analysis['issues']:
            st.write(f"• {issue.replace('-', ' ').title()}")
    
    with col2:
        st.write("**Risk Factors:**")
        for risk in analysis['risk_factors']:
            st.write(f"• {risk}")


def render_ai_recommendations_tab(pod, analysis, llm_rec):
    """Render AI recommendations tab."""
    if not llm_rec:
        st.error("Failed to load AI recommendations.")
        return
    
    st.subheader("🤖 AI-Powered Recommendations")
    
    # Summary
    st.write("**Summary:**")
    st.info(llm_rec.get('summary', 'No summary available'))
    
    # Recommendations
    st.write("**Specific Recommendations:**")
    for i, rec in enumerate(llm_rec.get('recommendations', []), 1):
        with st.expander(f"Recommendation {i}: {rec.get('resource_type', 'Unknown').replace('_', ' ').title()}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Current Value:** {rec.get('current_value', 'N/A')}")
                st.write(f"**Recommended Value:** {rec.get('recommended_value', 'N/A')}")
                st.write(f"**Risk Level:** {rec.get('risk_level', 'Unknown').title()}")
            
            with col2:
                st.write(f"**Reasoning:** {rec.get('reasoning', 'No reasoning provided')}")
                st.write(f"**Impact:** {rec.get('impact', 'No impact information')}")
    
    # Overall assessment
    st.write("**Overall Assessment:**")
    st.success(llm_rec.get('overall_assessment', 'No assessment available'))


def render_yaml_comparison_tab(pod, analysis, llm_rec):
    """Render YAML comparison tab."""
    if not llm_rec:
        st.error("Failed to load recommendations for YAML generation.")
        return
    
    yaml_gen = YAMLGenerator()
    
    # Generate YAML files
    current_yaml = yaml_gen.generate_current_manifest(pod)
    optimized_yaml = yaml_gen.generate_optimized_manifest(pod, llm_rec.get('recommendations', []))
    patch_yaml = yaml_gen.generate_patch_manifest(pod, llm_rec.get('recommendations', []))
    kubectl_command = yaml_gen.generate_kubectl_patch_command(pod, llm_rec.get('recommendations', []))
    
    # Create tabs for different YAML views
    yaml_tab1, yaml_tab2, yaml_tab3, yaml_tab4 = st.tabs(["Current", "Optimized", "Patch", "Command"])
    
    with yaml_tab1:
        st.subheader("📄 Current Manifest")
        st.code(current_yaml, language='yaml')
    
    with yaml_tab2:
        st.subheader("✨ Optimized Manifest")
        st.code(optimized_yaml, language='yaml')
    
    with yaml_tab3:
        st.subheader("🔧 Patch Manifest")
        st.code(patch_yaml, language='yaml')
    
    with yaml_tab4:
        st.subheader("⚡ kubectl Patch Command")
        st.code(kubectl_command, language='bash')
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download Patch YAML",
                data=patch_yaml,
                file_name=f"{pod['name']}-patch.yaml",
                mime="text/yaml"
            )
        
        with col2:
            st.download_button(
                label="📥 Download Optimized Manifest",
                data=optimized_yaml,
                file_name=f"{pod['name']}-optimized.yaml",
                mime="text/yaml"
            )


def render_trends_tab(pod):
    """Render trends tab with historical data."""
    st.subheader("📈 Resource Usage Trends")
    
    # Prepare historical data
    historical = pod['historical_data']
    df = pd.DataFrame(historical)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('CPU Usage Over Time', 'Memory Usage Over Time'),
        vertical_spacing=0.1
    )
    
    # CPU usage plot
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['cpu_usage'],
            mode='lines',
            name='CPU Usage',
            line=dict(color='#1f77b4')
        ),
        row=1, col=1
    )
    
    # Memory usage plot
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['memory_usage'],
            mode='lines',
            name='Memory Usage',
            line=dict(color='#ff7f0e')
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text=f"Resource Usage Trends - {pod['name']}"
    )
    
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="CPU Usage (millicores)", row=1, col=1)
    fig.update_yaxes(title_text="Memory Usage (MB)", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main application function."""
    # Header
    st.markdown('<h1 class="main-header">🕹️ Kubernetes AI Copilot</h1>', unsafe_allow_html=True)
    st.markdown("**AI-powered resource optimization for your Kubernetes clusters**")
    
    # Sidebar
    render_sidebar()
    
    # Main content
    if st.session_state.cluster_data is None:
        st.info("👈 Use the sidebar to load cluster data and start analyzing your Kubernetes resources!")
        return
    
    # Overview cards
    render_overview_cards()
    
    st.divider()
    
    # Cluster heatmap
    render_cluster_heatmap()
    
    st.divider()
    
    # Recommendations table
    render_recommendations_table()
    
    st.divider()
    
    # Detailed analysis
    render_detailed_analysis()


if __name__ == "__main__":
    main()
