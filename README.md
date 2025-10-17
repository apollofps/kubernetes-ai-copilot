# 🕹️ Kubernetes AI Copilot

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com)
[![Claude](https://img.shields.io/badge/Anthropic-Claude-orange.svg)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-powered Kubernetes resource optimization tool that analyzes pod metrics and provides intelligent recommendations using GPT-4/Claude for cost reduction and performance improvement.**

## ✨ Features

- 📊 **Real-time Cluster Monitoring** - Mock data simulation with realistic metrics
- 🤖 **AI-Powered Recommendations** - OpenAI GPT-4 and Anthropic Claude integration
- 📈 **Interactive Dashboard** - Streamlit-based web interface with visualizations
- 🔧 **YAML Generation** - Automatic generation of optimized resource configurations
- 📋 **Resource Analysis** - Identify over-provisioned and under-provisioned workloads
- 💰 **Cost Optimization** - Calculate potential savings and ROI
- 🎯 **Risk Assessment** - Evaluate implementation risks and mitigation strategies

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/kubernetes-ai-copilot.git
   cd kubernetes-ai-copilot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys (Optional)**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI and/or Anthropic API keys
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Open in Browser**
   Navigate to `http://localhost:8501`

### Demo Mode
Run the demo script to see all features without API keys:
```bash
python3 demo.py
```

## Configuration

The application supports both OpenAI and Anthropic Claude APIs. Configure your preferred provider in the `.env` file:

- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key  
- `DEFAULT_LLM_PROVIDER` - Set to "openai" or "anthropic"

## Mock Data

This POC uses realistic mock data including:
- 3-5 namespaces with 10-20 pods each
- Various workload types (microservices, databases, batch jobs)
- Resource utilization patterns and issues
- Historical metrics for trend analysis

## Project Structure

```
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── src/
│   ├── mock_data.py         # Mock cluster data generation
│   ├── metrics_analyzer.py  # Resource analysis engine
│   ├── llm_client.py        # LLM integration
│   ├── yaml_generator.py    # YAML diff generation
│   └── recommendations.py   # Recommendation processing
└── config/
    └── mock_clusters.yaml   # Mock cluster configurations
```

## Usage

1. **Select LLM Provider** - Choose between OpenAI or Claude in the sidebar
2. **Filter Data** - Use namespace and severity filters to focus on specific issues
3. **Review Recommendations** - Browse AI-generated optimization suggestions
4. **Analyze Details** - Click on recommendations for detailed analysis and YAML diffs
5. **Export Changes** - Copy or download optimized YAML configurations

## 🛠️ Technology Stack

- **Frontend**: Streamlit, Plotly
- **Backend**: Python 3.9+
- **AI/ML**: OpenAI GPT-4, Anthropic Claude
- **Data Processing**: Pandas, NumPy
- **Configuration**: PyYAML, python-dotenv
- **Visualization**: Plotly, Streamlit Charts

## 📊 Demo Results

The application successfully demonstrates:
- ✅ **41 pods** generated across 4 namespaces
- ✅ **73.8% overall efficiency** with optimization opportunities
- ✅ **$2,577.53/month** in potential savings identified
- ✅ **1,508.8% annual ROI** with 0.8-month payback period
- ✅ **Complete YAML generation** with kubectl commands

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API
- Streamlit team for the amazing web framework
- Kubernetes community for inspiration
