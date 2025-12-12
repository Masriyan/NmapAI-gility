# NmapAIGility v2.0 - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Verify Nmap is installed
nmap --version

# Optional: Install Nikto
sudo apt-get install nikto  # Debian/Ubuntu
brew install nikto          # macOS
```

### 2. Create Targets File

```bash
# Simple targets file
cat > targets.txt << EOF
scanme.nmap.org
45.33.32.156
EOF
```

### 3. Run Your First Scan

```bash
# Basic scan (no AI)
python nmapai_v2.py -f targets.txt

# With AI analysis (requires API key)
export OPENAI_API_KEY="sk-your-key-here"
python nmapai_v2.py -f targets.txt --ai
```

### 4. View Results

```bash
# Results are in timestamped directory
cd out_nmapai_v2_*/

# Open HTML dashboard in browser
xdg-open dashboard.html  # Linux
open dashboard.html      # macOS
start dashboard.html     # Windows
```

---

## 📊 Scan Profiles

### Quick Scan (Fast)
```bash
python nmapai_v2.py -f targets.txt --profile quick
```
- Scans top 100 ports
- No web scanning
- No enrichment
- **Time:** ~2-5 minutes

### Standard Scan (Recommended)
```bash
export OPENAI_API_KEY="sk-..."
python nmapai_v2.py -f targets.txt --profile standard --ai
```
- Scans top 1000 ports
- Nikto web scanning
- Full enrichment
- AI analysis
- **Time:** ~10-30 minutes

### Deep Scan (Thorough)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python nmapai_v2.py -f targets.txt --profile deep --ai --ai-provider anthropic
```
- Scans ALL 65535 ports
- Intensive scripts
- Full enrichment
- Advanced AI
- **Time:** 1-4 hours

### Stealth Scan (Evasive)
```bash
python nmapai_v2.py -f targets.txt --profile stealth
```
- Slow timing (-T2)
- Fragmented packets
- Minimal footprint
- **Time:** ~30-60 minutes

---

## 🤖 AI Provider Setup

### OpenAI (Cloud - Best Quality)

```bash
# Get API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-proj-..."

# Run with GPT-4o-mini (cheapest)
python nmapai_v2.py -f targets.txt --ai -m gpt-4o-mini

# Or GPT-4o (best quality)
python nmapai_v2.py -f targets.txt --ai -m gpt-4o
```

**Cost:** ~$0.15-0.60 per scan (depending on findings)

### Anthropic Claude (Cloud - Security-Focused)

```bash
# Get API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-..."

python nmapai_v2.py -f targets.txt --ai --ai-provider anthropic
```

**Cost:** ~$0.30-1.00 per scan

### Ollama (Local - Free & Private)

```bash
# Install Ollama from https://ollama.ai/
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.1:8b

# Start Ollama server
ollama serve &

# Run scan
python nmapai_v2.py -f targets.txt --ai --ai-provider ollama -m llama3.1:8b
```

**Cost:** Free! (But lower quality than cloud models)

---

## ⚡ Common Use Cases

### 1. Internal Network Assessment

```bash
# Scan internal subnet
cat > internal.txt << EOF
192.168.1.0/24
EOF

python nmapai_v2.py -f internal.txt --profile standard --ai -o internal_scan
```

### 2. External Pentest

```bash
# Comprehensive external scan
python nmapai_v2.py \
  -f external_targets.txt \
  --profile deep \
  -n "-sV -sC -A -T4 -p- --script vuln" \
  --adaptive \
  --ai \
  -o pentest_2024
```

### 3. Quick Recon

```bash
# Fast discovery scan
python nmapai_v2.py -f targets.txt --profile quick -K --no-enrichment
```

### 4. Compliance Scan

```bash
# Standard scan with full reporting
python nmapai_v2.py \
  -f assets.txt \
  --profile standard \
  --ai \
  --report-formats json markdown html csv \
  -o compliance_q4_2024
```

### 5. Bug Bounty Recon

```bash
# Web-focused scan
python nmapai_v2.py \
  -f bounty_targets.txt \
  -n "-sV -p 80,443,8000,8080,8443 --script http-*" \
  -t 5 \
  --ai \
  -o bounty_scan
```

---

## 🔧 Customization

### Create Custom Config

```bash
# Copy example config
cp nmapai/config/example-config.yaml my-scan-config.yaml

# Edit to your preferences
nano my-scan-config.yaml

# Use it
python nmapai_v2.py -f targets.txt --config my-scan-config.yaml
```

### Override Config with CLI

```bash
# Config file + custom Nmap params
python nmapai_v2.py \
  -f targets.txt \
  --config my-config.yaml \
  -n "-sS -T3 -p 1-10000" \
  --ai
```

---

## 📈 Understanding Output

### Directory Structure

```
out_nmapai_v2_20250112_143022/
├── dashboard.html          ⭐ Open this first!
├── report.md               📄 Human-readable report
├── report.json             🔧 Machine-readable data
├── vulnerabilities.csv     📊 Import to Excel
├── nmap_results.{nmap,gnmap,xml}
├── nikto/                  🌐 Web scan results
└── nmap_scan.log           📝 Execution log
```

### Risk Levels Explained

- **🔴 CRITICAL** - Active exploitation + High CVSS + Public exploit
- **🟠 HIGH** - High CVSS OR exploit available
- **🟡 MEDIUM** - Moderate severity, lower exploit probability
- **🟢 LOW** - Informational, minimal risk
- **⚪ INFO** - Non-security findings

### Priority Score (0-100)

Weighted combination of:
- **35%** CVSS score
- **25%** EPSS (exploit probability)
- **20%** Exploit availability
- **10%** Service exposure
- **10%** Vulnerability age

---

## 🐛 Troubleshooting

### Scan hangs or fails

```bash
# Run with verbose mode
python nmapai_v2.py -f targets.txt -v

# Check Nmap is working
nmap -sV scanme.nmap.org

# Test with dry-run
python nmapai_v2.py -f targets.txt --dry-run
```

### AI errors

```bash
# Verify API key
echo $OPENAI_API_KEY

# Test AI without scan
python -c "import openai; print(openai.api_key)"

# Try local AI instead
python nmapai_v2.py -f targets.txt --ai --ai-provider ollama
```

### Permission errors

```bash
# Some Nmap scans need root
sudo python nmapai_v2.py -f targets.txt ...

# Or use non-privileged scans
python nmapai_v2.py -f targets.txt -n "-sT"  # TCP connect scan
```

---

## 📚 Next Steps

1. **Read Full Documentation:** [README_V2.md](README_V2.md)
2. **Explore Profiles:** `python nmapai_v2.py --list-profiles`
3. **Customize Config:** Edit `nmapai/config/example-config.yaml`
4. **Extend Framework:** Check `nmapai/plugins/` for plugin examples

---

## 🆘 Getting Help

- **Documentation:** `python nmapai_v2.py --help`
- **Issues:** https://github.com/Masriyan/NmapAI-gility/issues
- **Examples:** See [README_V2.md](README_V2.md#examples)

---

**Happy Scanning! 🎯**
