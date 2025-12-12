# 🚀 Get Started with NmapAIGility v2.0

## Welcome! 👋

Congratulations on choosing NmapAIGility v2.0 - your new enterprise-grade security scanning framework!

This guide will get you up and running in **5 minutes**.

---

## 📦 Step 1: Installation (2 minutes)

### Install Python Dependencies

```bash
cd /home/sudo3rs/Documents/PrivateTools/NmapAIGility

# Install required packages
pip install -r requirements.txt

# Verify installation
python verify_installation.py
```

### Verify System Tools

```bash
# Check Nmap is installed
nmap --version

# Install if missing (Debian/Ubuntu)
sudo apt-get install nmap

# Install Nikto (optional, for web scanning)
sudo apt-get install nikto
```

---

## 🔑 Step 2: API Key Setup (1 minute)

Choose your AI provider:

### Option A: OpenAI (Recommended)

```bash
# Get API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-proj-your-key-here"

# Make it permanent (optional)
echo 'export OPENAI_API_KEY="sk-proj-your-key"' >> ~/.bashrc
```

### Option B: Anthropic Claude

```bash
# Get API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Option C: Ollama (Free, Local)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.1:8b

# Start server
ollama serve &
```

---

## 🎯 Step 3: First Scan (2 minutes)

### Create Targets File

```bash
# Create a simple targets file
cat > my_targets.txt << EOF
scanme.nmap.org
45.33.32.156
EOF
```

### Run Your First Scan

```bash
# Basic scan (no AI)
python nmapai_v2.py -f my_targets.txt --profile quick

# With AI analysis (OpenAI)
python nmapai_v2.py -f my_targets.txt --profile standard --ai

# With AI (Anthropic Claude)
python nmapai_v2.py -f my_targets.txt --profile standard --ai --ai-provider anthropic

# With AI (Local Ollama)
python nmapai_v2.py -f my_targets.txt --profile standard --ai --ai-provider ollama
```

---

## 📊 Step 4: View Results

```bash
# Results are in timestamped directory
cd out_nmapai_v2_*/

# Open interactive HTML dashboard
xdg-open dashboard.html     # Linux
open dashboard.html         # macOS
start dashboard.html        # Windows

# Or view markdown report
cat report.md | less
```

---

## 🎓 What's Next?

### Learn the Basics (5-10 minutes)

```bash
# See all available profiles
python nmapai_v2.py --list-profiles

# View help and all options
python nmapai_v2.py --help

# Read the quick start guide
cat QUICKSTART.md
```

### Try Different Profiles

```bash
# Quick reconnaissance (2-5 min)
python nmapai_v2.py -f targets.txt --profile quick

# Standard comprehensive scan (10-30 min)
python nmapai_v2.py -f targets.txt --profile standard --ai

# Deep thorough scan (1-4 hrs)
python nmapai_v2.py -f targets.txt --profile deep --ai

# Stealth evasive scan (30-60 min)
python nmapai_v2.py -f targets.txt --profile stealth
```

### Create Custom Config

```bash
# Copy example config
cp nmapai/config/example-config.yaml my-config.yaml

# Edit to your preferences
nano my-config.yaml

# Use it
python nmapai_v2.py -f targets.txt --config my-config.yaml
```

---

## 🔧 Common Use Cases

### 1. Internal Network Assessment

```bash
# Scan internal network
cat > internal.txt << EOF
192.168.1.0/24
10.0.0.0/24
EOF

python nmapai_v2.py -f internal.txt --profile standard --ai
```

### 2. External Pentest

```bash
# Deep scan of external assets
python nmapai_v2.py \
  -f external_targets.txt \
  --profile deep \
  --adaptive \
  --ai \
  -o pentest_2025
```

### 3. Quick Vulnerability Check

```bash
# Fast scan without web testing
python nmapai_v2.py \
  -f targets.txt \
  --profile quick \
  -K \
  --no-enrichment
```

### 4. Compliance Scan

```bash
# Standard scan with all reports
python nmapai_v2.py \
  -f assets.txt \
  --profile standard \
  --ai \
  --report-formats json markdown html csv \
  -o compliance_q1_2025
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'aiohttp'"

```bash
pip install -r requirements.txt
```

### "Nmap not found"

```bash
# Install Nmap
sudo apt-get install nmap   # Debian/Ubuntu
brew install nmap            # macOS
```

### "OPENAI_API_KEY not set"

```bash
export OPENAI_API_KEY="sk-your-key"
```

### "Permission denied"

```bash
# Some Nmap scans need root
sudo python nmapai_v2.py -f targets.txt ...
```

### "Ollama not responding"

```bash
# Start Ollama server
ollama serve &

# Verify it's running
curl http://localhost:11434/api/tags
```

---

## 📚 Documentation

### Must-Read
1. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute guide with examples
2. **[README_V2.md](README_V2.md)** - Complete documentation

### Reference
3. **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Upgrading from v1
4. **[CHANGELOG_V2.md](CHANGELOG_V2.md)** - What's new in v2
5. **[SUMMARY.md](SUMMARY.md)** - Project overview

---

## 💡 Pro Tips

### Tip 1: Use Profiles for Common Scenarios
```bash
# Don't memorize Nmap flags, use profiles!
python nmapai_v2.py -f targets.txt --profile standard --ai
```

### Tip 2: Save Configurations
```bash
# Create reusable configs for different environments
cp nmapai/config/example-config.yaml prod-config.yaml
python nmapai_v2.py -f targets.txt --config prod-config.yaml
```

### Tip 3: Try Local AI First (Free)
```bash
# Ollama is free and works offline
ollama pull llama3.1:8b
python nmapai_v2.py -f targets.txt --ai --ai-provider ollama
```

### Tip 4: Optimize for Speed
```bash
# Skip enrichment for faster scans
python nmapai_v2.py -f targets.txt --no-nvd --no-epss --no-exploitdb
```

### Tip 5: Get NVD API Key (Free)
```bash
# Faster enrichment with API key
# Get from: https://nvd.nist.gov/developers/request-an-api-key
python nmapai_v2.py -f targets.txt --nvd-api-key "your-key"
```

---

## 🎯 Quick Command Reference

```bash
# Basic scan
python nmapai_v2.py -f targets.txt

# With AI (OpenAI)
python nmapai_v2.py -f targets.txt --ai

# With AI (Claude)
python nmapai_v2.py -f targets.txt --ai --ai-provider anthropic

# With AI (Ollama - Free)
python nmapai_v2.py -f targets.txt --ai --ai-provider ollama

# Use profile
python nmapai_v2.py -f targets.txt --profile standard --ai

# Custom Nmap params
python nmapai_v2.py -f targets.txt -n "-sV -sC -A -T4 -p-"

# Use config file
python nmapai_v2.py -f targets.txt --config my-config.yaml

# Disable Nikto
python nmapai_v2.py -f targets.txt -K

# Custom output dir
python nmapai_v2.py -f targets.txt -o my_scan_results

# List profiles
python nmapai_v2.py --list-profiles

# Help
python nmapai_v2.py --help
```

---

## 🎓 Learning Path

### Beginner (Day 1)
1. ✅ Install dependencies
2. ✅ Run basic scan
3. ✅ View HTML dashboard
4. ✅ Try different profiles

### Intermediate (Week 1)
1. ✅ Set up AI provider
2. ✅ Create custom config file
3. ✅ Run scans with enrichment
4. ✅ Understand risk scoring

### Advanced (Month 1)
1. ✅ Write custom plugins
2. ✅ Integrate into CI/CD
3. ✅ Automate regular scans
4. ✅ Custom reporting templates

---

## 🆘 Getting Help

### Documentation
- **Full docs:** [README_V2.md](README_V2.md)
- **Quick start:** [QUICKSTART.md](QUICKSTART.md)
- **Help command:** `python nmapai_v2.py --help`

### Community
- **Issues:** https://github.com/Masriyan/NmapAI-gility/issues
- **Discussions:** https://github.com/Masriyan/NmapAI-gility/discussions

### Verification
```bash
# Run verification script
python verify_installation.py
```

---

## ✅ Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Nmap installed
- [ ] API key configured (for AI features)
- [ ] Verification script passed
- [ ] First scan completed
- [ ] HTML dashboard viewed
- [ ] Documentation reviewed

---

## 🎉 You're Ready!

You now have a powerful enterprise-grade security scanning framework at your fingertips!

**Start scanning:**
```bash
python nmapai_v2.py -f targets.txt --profile standard --ai
```

**Enjoy! 🚀**

---

*NmapAIGility v2.0 - Enterprise Security Scanning Framework*
*Built with ❤️ by sudo3rs (Riyan) & Kang Ali*
