# NmapAIGility v2.0 - Documentation Index

**Welcome to NmapAIGility v2.0!** This index will help you navigate all available documentation.

---

## 🚀 Getting Started

### For First-Time Users

1. **[GET_STARTED.md](GET_STARTED.md)** ⭐ **START HERE**
   - 5-minute installation guide
   - First scan walkthrough
   - Quick command reference
   - Common use cases

2. **[QUICKSTART.md](QUICKSTART.md)**
   - Detailed quick start guide
   - Scan profile examples
   - AI provider setup
   - Troubleshooting tips

3. **[verify_installation.py](verify_installation.py)**
   - Run: `python verify_installation.py`
   - Checks all dependencies
   - Verifies installation

---

## 📚 Complete Documentation

### Main Documentation

4. **[README_V2.md](README_V2.md)** 📖 **COMPREHENSIVE GUIDE**
   - Complete feature documentation
   - Architecture overview
   - Configuration guide
   - API reference
   - Troubleshooting
   - Examples

### Project Information

5. **[SUMMARY.md](SUMMARY.md)** 📊
   - Project overview
   - What was built
   - Feature comparison (v1 vs v2)
   - Statistics and metrics
   - Architecture explanation

6. **[CHANGELOG_V2.md](CHANGELOG_V2.md)** 📝
   - What's new in v2.0
   - Breaking changes
   - Feature additions
   - Bug fixes
   - Future roadmap

### Migration

7. **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** 🔄
   - Upgrading from v1 to v2
   - Breaking changes explained
   - Side-by-side comparisons
   - Migration steps
   - Common issues

---

## 🔧 Configuration & Setup

### Configuration Files

8. **[nmapai/config/example-config.yaml](nmapai/config/example-config.yaml)** ⚙️
   - Complete configuration example
   - All options documented
   - Copy and customize for your needs

### Setup Files

9. **[requirements.txt](requirements.txt)**
   - Python dependencies
   - Install: `pip install -r requirements.txt`

10. **[setup.py](setup.py)**
    - Package installation
    - Install: `pip install -e .`

---

## 💻 Code Reference

### Main Script

11. **[nmapai_v2.py](nmapai_v2.py)** - Enhanced main entry point
    - CLI interface
    - Profile management
    - Configuration loading
    - Run: `python nmapai_v2.py --help`

### Core Modules

12. **[nmapai/core/](nmapai/core/)**
    - `base_plugin.py` - Plugin base classes
    - `scanner_manager.py` - Orchestration engine
    - `vulnerability_engine.py` - Risk scoring
    - `ai_engine.py` - AI correlation
    - `report_generator.py` - Multi-format reports

### Plugins

13. **[nmapai/plugins/](nmapai/plugins/)**
    - **scanners/** - Nmap, Nikto plugins
    - **ai_providers/** - OpenAI, Anthropic, Ollama
    - **enrichers/** - NVD, EPSS, ExploitDB

### Utilities

14. **[nmapai/utils/](nmapai/utils/)**
    - `config_manager.py` - Configuration & profiles

---

## 📖 Reading Paths

### Path 1: Quick User (5 minutes)
```
1. GET_STARTED.md
2. Run: python nmapai_v2.py -f targets.txt
3. Open: dashboard.html
```

### Path 2: Thorough User (30 minutes)
```
1. GET_STARTED.md
2. QUICKSTART.md
3. README_V2.md (skim)
4. Run examples
```

### Path 3: Developer (1-2 hours)
```
1. SUMMARY.md (architecture)
2. README_V2.md (complete)
3. CHANGELOG_V2.md
4. Review code in nmapai/
```

### Path 4: Migrating from v1 (30 minutes)
```
1. MIGRATION_GUIDE.md
2. CHANGELOG_V2.md
3. Test v2 alongside v1
4. Migrate workflows
```

---

## 🎯 By Task

### I want to...

**Install and run first scan**
→ [GET_STARTED.md](GET_STARTED.md)

**Learn all features**
→ [README_V2.md](README_V2.md)

**Migrate from v1**
→ [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

**Understand the architecture**
→ [SUMMARY.md](SUMMARY.md)

**See what's new**
→ [CHANGELOG_V2.md](CHANGELOG_V2.md)

**Configure custom scans**
→ [nmapai/config/example-config.yaml](nmapai/config/example-config.yaml)

**Write a plugin**
→ [nmapai/core/base_plugin.py](nmapai/core/base_plugin.py) + [README_V2.md](README_V2.md#architecture)

**Troubleshoot issues**
→ [QUICKSTART.md](QUICKSTART.md#troubleshooting) + [README_V2.md](README_V2.md#troubleshooting)

**Use AI providers**
→ [README_V2.md](README_V2.md#ai-providers) + [QUICKSTART.md](QUICKSTART.md#ai-provider-setup)

**Understand risk scoring**
→ [nmapai/core/vulnerability_engine.py](nmapai/core/vulnerability_engine.py)

**See examples**
→ [README_V2.md](README_V2.md#examples) + [QUICKSTART.md](QUICKSTART.md#common-use-cases)

---

## 📂 File Organization

```
NmapAIGility/
│
├── Documentation (You are here!)
│   ├── INDEX.md              ← This file
│   ├── GET_STARTED.md        ← Start here
│   ├── QUICKSTART.md         ← Quick guide
│   ├── README_V2.md          ← Complete docs
│   ├── SUMMARY.md            ← Overview
│   ├── CHANGELOG_V2.md       ← What's new
│   ├── MIGRATION_GUIDE.md    ← v1 → v2
│   └── README.md             ← Original v1 README
│
├── Main Scripts
│   ├── nmapai_v2.py          ← New enhanced version
│   ├── nmapai.py             ← Original v1 (still works)
│   └── verify_installation.py
│
├── Configuration
│   ├── requirements.txt
│   ├── setup.py
│   └── nmapai/config/example-config.yaml
│
└── Source Code
    └── nmapai/
        ├── core/             ← Core engines
        ├── plugins/          ← Extensible plugins
        ├── utils/            ← Utilities
        └── config/           ← Configuration files
```

---

## 🆘 Quick Help

### Installation Issues
```bash
python verify_installation.py
pip install -r requirements.txt
```

### Command Help
```bash
python nmapai_v2.py --help
python nmapai_v2.py --list-profiles
```

### Documentation Help
- **Complete docs:** `cat README_V2.md`
- **Quick start:** `cat QUICKSTART.md`
- **Get started:** `cat GET_STARTED.md`

---

## 🔗 External Resources

### Tools
- **Nmap:** https://nmap.org/
- **Nikto:** https://cirt.net/Nikto2
- **DursVuln:** https://github.com/roomkangali/DursVulnNSE

### AI Providers
- **OpenAI:** https://platform.openai.com/
- **Anthropic:** https://console.anthropic.com/
- **Ollama:** https://ollama.ai/

### Vulnerability Databases
- **NVD:** https://nvd.nist.gov/
- **EPSS:** https://www.first.org/epss/
- **ExploitDB:** https://www.exploit-db.com/

---

## 📊 Documentation Statistics

| Document | Size | Purpose | Audience |
|----------|------|---------|----------|
| GET_STARTED.md | ~5KB | Quick start | Beginners |
| QUICKSTART.md | ~6KB | Detailed guide | Users |
| README_V2.md | ~16KB | Complete reference | All |
| SUMMARY.md | ~13KB | Overview | Developers |
| MIGRATION_GUIDE.md | ~9KB | Upgrading | v1 users |
| CHANGELOG_V2.md | ~8KB | Release notes | All |
| INDEX.md | ~3KB | Navigation | All |

**Total:** ~60KB of documentation

---

## ✅ Checklist

Use this checklist to track your progress:

### Installation
- [ ] Read GET_STARTED.md
- [ ] Install dependencies
- [ ] Run verify_installation.py
- [ ] Configure API key

### First Scan
- [ ] Create targets file
- [ ] Run basic scan
- [ ] View HTML dashboard
- [ ] Review Markdown report

### Learning
- [ ] Try scan profiles
- [ ] Read QUICKSTART.md
- [ ] Skim README_V2.md
- [ ] Review example config

### Advanced
- [ ] Create custom config
- [ ] Try multiple AI providers
- [ ] Understand risk scoring
- [ ] Review plugin code

---

## 🎓 Recommended Learning Path

**Day 1 (30 minutes)**
1. Read [GET_STARTED.md](GET_STARTED.md)
2. Install and verify
3. Run first scan
4. View dashboard

**Day 2 (1 hour)**
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Try different profiles
3. Set up AI provider
4. Run scans with AI

**Week 1 (2-3 hours)**
1. Read [README_V2.md](README_V2.md)
2. Create custom config
3. Understand risk scoring
4. Integrate into workflow

**Month 1 (ongoing)**
1. Explore [SUMMARY.md](SUMMARY.md)
2. Review plugin code
3. Consider custom plugins
4. Contribute improvements

---

## 💡 Pro Tips

1. **Always start with GET_STARTED.md** - It's designed for first-time users
2. **Use verify_installation.py** - Catches issues early
3. **Try profiles before custom configs** - Profiles cover most use cases
4. **Read QUICKSTART.md examples** - Learn by doing
5. **Keep README_V2.md as reference** - Comprehensive information
6. **Check CHANGELOG_V2.md for updates** - Stay current

---

## 🚀 Get Started Now!

Ready to begin? Start here:

```bash
# 1. Read the quick start
cat GET_STARTED.md

# 2. Verify installation
python verify_installation.py

# 3. Run your first scan
python nmapai_v2.py -f targets.txt --profile standard --ai

# 4. View results
xdg-open out_nmapai_v2_*/dashboard.html
```

---

**Happy Scanning! 🎯**

*NmapAIGility v2.0 - Enterprise Security Scanning Framework*
*Documentation by sudo3rs (Riyan)*
