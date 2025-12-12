# NmapAIGility v2.0 - Enterprise Security Scanning Framework

> **Powerful, AI-Enhanced Security Assessment Tool with Advanced Vulnerability Intelligence**

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Version](https://img.shields.io/badge/Version-2.0.0-orange)

---

## 🚀 What's New in v2.0

NmapAIGility v2.0 is a **complete rewrite** with enterprise-grade features:

### **🏗️ Architecture Improvements**
- ✅ **Modular Plugin System** - Easy to extend with custom scanners, AI providers, enrichers
- ✅ **Async/Await Throughout** - True concurrent execution for maximum performance
- ✅ **Clean Separation of Concerns** - Core engines, plugins, utilities properly separated

### **🤖 Advanced AI Integration**
- ✅ **Multi-Model Support** - OpenAI (GPT-4, GPT-4o), Anthropic (Claude), Ollama (local LLMs)
- ✅ **Streaming Responses** - Real-time AI analysis output
- ✅ **Intelligent Correlation** - AI-powered vulnerability chain analysis
- ✅ **Context-Aware Analysis** - Enriched data for better AI insights

### **🔍 Vulnerability Intelligence**
- ✅ **NVD Integration** - Fetch CVSS scores, descriptions, references from National Vulnerability Database
- ✅ **EPSS Scoring** - Exploit Prediction Scoring System for real-world exploit probability
- ✅ **ExploitDB Search** - Automatic exploit availability detection
- ✅ **Smart Prioritization** - Multi-factor risk scoring (CVSS + EPSS + exploits + exposure + age)

### **📊 Enhanced Reporting**
- ✅ **Interactive HTML Dashboard** - Beautiful charts, tables, and visualizations
- ✅ **Multiple Formats** - JSON, Markdown, CSV, HTML
- ✅ **Executive Summaries** - High-level security posture overview
- ✅ **Prioritized Recommendations** - Actionable remediation steps ranked by risk

### **⚙️ Smart Features**
- ✅ **Scan Profiles** - Pre-configured profiles (quick, standard, deep, stealth)
- ✅ **Adaptive Scanning** - Intelligent target selection based on initial discovery
- ✅ **Configuration Management** - YAML/JSON config files, profile system
- ✅ **Rich Progress Display** - Beautiful terminal UI with progress bars

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Scan Profiles](#-scan-profiles)
- [AI Providers](#-ai-providers)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Examples](#-examples)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Scanning
- **Nmap Integration** - Full Nmap feature support with progress tracking
- **Nikto Web Scanning** - Automated HTTP/HTTPS service scanning
- **DursVuln NSE** - Local CVE enrichment (maintained from v1)

### AI-Powered Analysis
- **OpenAI (GPT-4, GPT-4o-mini)** - Cloud-based advanced analysis
- **Anthropic Claude** - Alternative cloud AI with excellent security knowledge
- **Ollama** - Local/offline LLM support (llama3.1, mistral, etc.)
- **Streaming Mode** - Real-time AI response output

### Vulnerability Intelligence
- **NVD API** - CVSS scores, severity ratings, detailed descriptions
- **EPSS API** - Real-world exploit probability metrics
- **ExploitDB** - Public exploit availability checking
- **Risk Scoring** - Weighted multi-factor vulnerability prioritization

### Reporting & Outputs
- **HTML Dashboard** - Interactive web dashboard with charts
- **Markdown Reports** - Human-readable formatted reports
- **JSON Export** - Machine-readable structured data
- **CSV Export** - Spreadsheet-compatible vulnerability lists

### Operational Features
- **Scan Profiles** - Quick, Standard, Deep, Stealth pre-configurations
- **Config Files** - YAML/JSON configuration support
- **Adaptive Mode** - Smart follow-up scanning based on findings
- **Rich UI** - Beautiful terminal interface with progress tracking

---

## 🔧 Installation

### Prerequisites

**Required:**
- Python 3.9 or higher
- Nmap 7.94+ ([download](https://nmap.org/download.html))

**Optional:**
- Nikto (for web scanning)
- DursVuln NSE (for local CVE enrichment)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/Masriyan/NmapAI-gility.git
cd NmapAI-gility

# 2. Install Python dependencies
pip install -r requirements.txt

# Or install with setup.py
pip install -e .

# 3. Verify installation
python nmapai_v2.py --help
```

### System Dependencies

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y nmap nikto

# macOS (Homebrew)
brew install nmap nikto

# Windows
# Download Nmap installer from https://nmap.org/download.html
# Add Nmap to your system PATH
```

---

## 🚀 Quick Start

### Basic Scan

```bash
# Create a targets file
echo "scanme.nmap.org" > targets.txt

# Run basic scan
python nmapai_v2.py -f targets.txt
```

### Scan with AI Analysis (OpenAI)

```bash
# Set API key
export OPENAI_API_KEY="sk-your-key-here"

# Run scan with AI
python nmapai_v2.py -f targets.txt --ai
```

### Use a Scan Profile

```bash
# Standard comprehensive scan
python nmapai_v2.py -f targets.txt --profile standard --ai

# Quick scan for rapid assessment
python nmapai_v2.py -f targets.txt --profile quick

# Deep thorough scan
python nmapai_v2.py -f targets.txt --profile deep --ai
```

---

## 📖 Usage

### Command Line Options

```
usage: nmapai_v2.py [-h] -f FILE [--profile {quick,standard,deep,stealth}]
                    [--config CONFIG] [-n NMAP_PARAMS] [--adaptive]
                    [-K] [-t THREADS] [-D] [-G] [-L DURSVULN_SCRIPT]
                    [-P DURSVULN_DB] [-S {LOW,MEDIUM,HIGH,CRITICAL}]
                    [-O {concise,full}] [-U] [-a]
                    [--ai-provider {openai,anthropic,ollama}] [-m MODEL]
                    [--ai-stream] [--ai-endpoint AI_ENDPOINT]
                    [--no-nvd] [--no-epss] [--no-exploitdb]
                    [--nvd-api-key NVD_API_KEY] [-o OUTPUT]
                    [--report-formats {json,markdown,html,csv} [{json,markdown,html,csv} ...]]
                    [-r] [-v] [--list-profiles]
```

### Key Arguments

| Argument | Description |
|----------|-------------|
| `-f, --file` | **Required.** Target list file (IP/hostname/CIDR, one per line) |
| `--profile` | Use predefined scan profile (quick/standard/deep/stealth) |
| `--config` | Load configuration from YAML/JSON file |
| `-n, --nmap` | Custom Nmap parameters (e.g., "-sV -T4 --top-ports 2000") |
| `-a, --ai` | Enable AI-powered analysis |
| `--ai-provider` | AI provider (openai/anthropic/ollama) |
| `-o, --output` | Output directory |
| `--list-profiles` | Show available scan profiles |

---

## 🎯 Scan Profiles

NmapAIGility v2 includes 4 pre-configured profiles:

### **Quick**
Fast reconnaissance scan
- Nmap: `-sV -T4 --top-ports 100`
- Nikto: Disabled
- Enrichment: Disabled
- AI: Disabled
- **Use case:** Quick network discovery

### **Standard** ⭐ Recommended
Comprehensive balanced scan
- Nmap: `-sV -sC -T4 --top-ports 1000`
- Nikto: Enabled (3 threads)
- Enrichment: NVD + EPSS + ExploitDB
- AI: Enabled (OpenAI)
- **Use case:** Regular security assessments

### **Deep**
Thorough intensive scan
- Nmap: `-sV -sC -A -T4 -p-` (all ports)
- Nikto: Enabled (5 threads)
- Enrichment: All sources
- AI: Enabled (Anthropic Claude)
- **Use case:** In-depth pentesting

### **Stealth**
Slow evasive scan
- Nmap: `-sS -T2 --top-ports 200 -f`
- Nikto: Disabled
- Enrichment: NVD only
- AI: Disabled
- **Use case:** Avoiding detection

---

## 🤖 AI Providers

### OpenAI (Default)

```bash
export OPENAI_API_KEY="sk-your-key"
python nmapai_v2.py -f targets.txt --ai --ai-provider openai -m gpt-4o-mini
```

**Supported Models:**
- `gpt-4o` - Most capable (expensive)
- `gpt-4o-mini` - Best value (default)
- `gpt-4-turbo` - Previous generation
- `gpt-3.5-turbo` - Fastest (cheapest)

### Anthropic Claude

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key"
python nmapai_v2.py -f targets.txt --ai --ai-provider anthropic -m claude-3-5-sonnet-20241022
```

**Supported Models:**
- `claude-3-5-sonnet-20241022` - Best for security analysis
- `claude-3-opus-20240229` - Most capable
- `claude-3-haiku-20240307` - Fastest

### Ollama (Local)

```bash
# Install Ollama: https://ollama.ai/
# Pull a model: ollama pull llama3.1:8b

python nmapai_v2.py -f targets.txt --ai --ai-provider ollama -m llama3.1:8b --ai-endpoint http://localhost:11434
```

**Supported Models:**
- `llama3.1:8b` - Recommended for security
- `mistral:7b` - Good alternative
- `codellama:13b` - Code-focused

**Advantages:**
- ✅ Free and private
- ✅ No API keys required
- ✅ Offline operation
- ❌ Lower quality than cloud models

---

## ⚙️ Configuration

### Configuration File

Create `config.yaml`:

```yaml
nmap:
  enabled: true
  nmap_params: "-sV -sC -T4 --top-ports 1500"
  adaptive_mode: true

nikto:
  enabled: true
  concurrency: 4

dursvuln:
  enabled: true
  use_global: true
  min_severity: "HIGH"

enrichers:
  nvd:
    enabled: true
    api_key: "your-nvd-api-key"  # Optional, for faster rate limits
  epss:
    enabled: true
  exploitdb:
    enabled: true

ai:
  enabled: true
  provider: "openai"
  model: "gpt-4o-mini"
  max_tokens: 2000
  temperature: 0.2

vulnerability_engine:
  scoring_weights:
    cvss: 0.35
    epss: 0.25
    exploit_available: 0.20
    service_exposure: 0.10
    age: 0.10

reporting:
  formats: ["json", "markdown", "html", "csv"]
```

Run with config:

```bash
python nmapai_v2.py -f targets.txt --config config.yaml
```

### Environment Variables

```bash
# AI API Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# NVD API Key (optional, for faster rate limits)
export NVD_API_KEY="your-nvd-key"

# Custom endpoints
export OPENAI_ENDPOINT="https://api.openai.com/v1/chat/completions"
export OLLAMA_ENDPOINT="http://localhost:11434"
```

---

## 🏗️ Architecture

### Project Structure

```
NmapAIGility/
├── nmapai_v2.py                    # Main entry point
├── nmapai/                         # Core package
│   ├── core/                       # Core engines
│   │   ├── base_plugin.py          # Plugin base classes
│   │   ├── scanner_manager.py      # Orchestration
│   │   ├── vulnerability_engine.py # Risk scoring
│   │   ├── ai_engine.py            # AI correlation
│   │   └── report_generator.py     # Reporting
│   ├── plugins/                    # Plugin system
│   │   ├── scanners/               # Scanner plugins
│   │   │   ├── nmap_scanner.py
│   │   │   └── nikto_scanner.py
│   │   ├── ai_providers/           # AI providers
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   └── ollama_provider.py
│   │   ├── enrichers/              # Vulnerability enrichers
│   │   │   ├── nvd_enricher.py
│   │   │   ├── epss_enricher.py
│   │   │   └── exploitdb_enricher.py
│   │   ├── reporters/              # Report generators
│   │   └── notifiers/              # Notification plugins
│   └── utils/                      # Utilities
│       └── config_manager.py       # Configuration
├── requirements.txt
├── setup.py
└── README_V2.md
```

### Plugin System

Easily extend NmapAIGility with custom plugins:

```python
from nmapai.core.base_plugin import ScannerPlugin

class CustomScanner(ScannerPlugin):
    @property
    def name(self) -> str:
        return "custom_scanner"

    async def validate(self) -> bool:
        # Check if scanner is available
        return True

    async def scan(self, targets, params):
        # Implement custom scanning logic
        return {"results": []}
```

---

## 💡 Examples

### Example 1: Standard Security Assessment

```bash
python nmapai_v2.py \
  -f corporate_assets.txt \
  --profile standard \
  --ai \
  -o results/corporate_scan
```

### Example 2: Deep Pentest with Custom Nmap

```bash
python nmapai_v2.py \
  -f targets.txt \
  -n "-sV -sC -A -T4 -p- --script vuln" \
  --adaptive \
  --ai \
  --ai-provider anthropic \
  -m claude-3-5-sonnet-20241022 \
  -o pentest_results
```

### Example 3: Quick Scan with Local AI

```bash
# Start Ollama
ollama serve &
ollama pull llama3.1:8b

# Run scan
python nmapai_v2.py \
  -f targets.txt \
  --profile quick \
  --ai \
  --ai-provider ollama \
  -m llama3.1:8b
```

### Example 4: Stealth Scan (No Web/AI)

```bash
python nmapai_v2.py \
  -f targets.txt \
  --profile stealth \
  -K \
  --no-epss \
  --no-exploitdb
```

### Example 5: Config File + Custom Options

```bash
python nmapai_v2.py \
  -f targets.txt \
  --config my-config.yaml \
  -n "-sV -T3 --top-ports 5000" \
  --ai-stream \
  -o custom_scan
```

---

## 📊 Output Structure

```
out_nmapai_v2_20250112_143022/
├── nmap_results.nmap              # Nmap normal output
├── nmap_results.gnmap             # Grepable format
├── nmap_results.xml               # XML format
├── nikto/                         # Nikto reports
│   ├── 192.168.1.100_80.html
│   └── 192.168.1.100_443.html
├── report.json                    # Full scan data (JSON)
├── report.md                      # Markdown report
├── dashboard.html                 # Interactive HTML dashboard ⭐
├── vulnerabilities.csv            # CSV export
└── nmap_scan.log                  # Execution log
```

**Open the dashboard:**
```bash
# Linux/Mac
xdg-open out_nmapai_v2_*/dashboard.html

# Windows
start out_nmapai_v2_*\dashboard.html
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Nmap not found"**
```bash
# Install Nmap
sudo apt-get install nmap  # Debian/Ubuntu
brew install nmap           # macOS

# Or download from https://nmap.org/download.html
```

**2. "OPENAI_API_KEY not set"**
```bash
export OPENAI_API_KEY="sk-your-key"
```

**3. "NVD API rate limit exceeded"**
```bash
# Get free API key from https://nvd.nist.gov/developers/request-an-api-key
python nmapai_v2.py -f targets.txt --nvd-api-key "your-key"
```

**4. "Ollama not responding"**
```bash
# Start Ollama
ollama serve

# Pull model
ollama pull llama3.1:8b

# Check endpoint
curl http://localhost:11434/api/tags
```

**5. "Permission denied" errors**
```bash
# Some Nmap scans require root
sudo python nmapai_v2.py -f targets.txt ...
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Additional scanner plugins (Masscan, Nuclei, etc.)
- [ ] More AI providers (Google Gemini, local models)
- [ ] PDF report generation
- [ ] Notification plugins (Slack, Discord, Email)
- [ ] Advanced attack chain detection
- [ ] SARIF output format
- [ ] Web UI for scan management

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **Nmap** - Gordon Lyon (Fyodor)
- **DursVuln** - Kang Ali (roomkangali)
- **Nikto** - CIRT.net
- **NVD** - NIST National Vulnerability Database
- **FIRST** - EPSS Project
- **ExploitDB** - Offensive Security
- **OpenAI, Anthropic, Ollama** - AI providers

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Masriyan/NmapAI-gility/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Masriyan/NmapAI-gility/discussions)

---

**⚠️ Legal Notice:** Only scan systems you own or have explicit authorization to test. Unauthorized scanning is illegal.

**Made with ❤️ by sudo3rs (Riyan) & Kang Ali**
