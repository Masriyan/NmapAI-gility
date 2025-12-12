# Changelog - NmapAIGility v2.0

## [2.0.0] - 2025-01-12

### 🎉 Major Release - Complete Rewrite

This is a **major version upgrade** with breaking changes and significant improvements.

---

## Added

### 🏗️ **Architecture**
- ✅ Modular plugin system with base classes
- ✅ Clean separation between core, plugins, and utilities
- ✅ Async/await implementation throughout
- ✅ Plugin lifecycle management (validate, execute, cleanup)

### 🤖 **AI Integration**
- ✅ Multi-model support: OpenAI, Anthropic Claude, Ollama
- ✅ Streaming responses for real-time output
- ✅ Configurable AI parameters (temperature, max_tokens, etc.)
- ✅ Custom AI endpoint support
- ✅ Intelligent vulnerability correlation

### 🔍 **Vulnerability Intelligence**
- ✅ NVD (National Vulnerability Database) integration
  - CVSS scores and severity ratings
  - Detailed vulnerability descriptions
  - CVE references and links
  - Optional API key for faster rate limits
- ✅ EPSS (Exploit Prediction Scoring System)
  - Real-world exploit probability metrics
  - Percentile rankings
  - Batch API support
- ✅ ExploitDB integration
  - Public exploit availability checking
  - Exploit metadata (type, platform, date)
  - Direct exploit links
- ✅ Multi-factor risk scoring engine
  - Weighted scoring (CVSS, EPSS, exploits, exposure, age)
  - Automated risk level classification
  - Prioritized remediation recommendations

### 📊 **Reporting**
- ✅ Interactive HTML dashboard with charts
  - Doughnut charts for vulnerability distribution
  - Sortable tables
  - Responsive design
  - Dark theme
- ✅ Enhanced Markdown reports
  - Executive summaries
  - Per-host breakdowns
  - Prioritized recommendations
  - AI analysis integration
- ✅ Structured JSON output
  - Complete scan metadata
  - Enriched vulnerability data
  - Machine-readable format
- ✅ CSV export for spreadsheet analysis

### ⚙️ **Configuration**
- ✅ Scan profiles (quick, standard, deep, stealth)
- ✅ YAML/JSON configuration file support
- ✅ Profile merging and overrides
- ✅ Default configuration management
- ✅ Environment variable support

### 🔧 **Scanning Features**
- ✅ Adaptive scanning mode
  - Intelligent follow-up scans
  - Service-based deep diving
  - Automatic interesting target detection
- ✅ Enhanced Nmap scanner plugin
  - XML parsing for structured data
  - Progress tracking improvements
  - Service fingerprint extraction
- ✅ Enhanced Nikto scanner plugin
  - JSON output support
  - Severity classification
  - Finding categorization

### 🎨 **User Experience**
- ✅ Rich terminal UI with progress bars
- ✅ Color-coded output
- ✅ Real-time progress tracking
- ✅ Spinner animations
- ✅ Beautiful ASCII banner
- ✅ Summary tables
- ✅ `--list-profiles` command

### 📚 **Documentation**
- ✅ Comprehensive README_V2.md
- ✅ Quick start guide (QUICKSTART.md)
- ✅ Migration guide (MIGRATION_GUIDE.md)
- ✅ Example configuration file
- ✅ Detailed API documentation
- ✅ Troubleshooting guide
- ✅ Usage examples

---

## Changed

### ⚠️ **Breaking Changes**
- 🔄 Script renamed: `nmapai.py` → `nmapai_v2.py`
- 🔄 Output directory: `out_nmapai_*` → `out_nmapai_v2_*`
- 🔄 Package structure completely reorganized
- 🔄 Configuration format changed (now supports YAML/JSON)
- 🔄 AI provider must be explicitly specified
- 🔄 Enrichment now enabled by default

### 📝 **Improvements**
- 🔧 Better error handling and logging
- 🔧 More efficient async operations
- 🔧 Improved code organization
- 🔧 Enhanced type hints
- 🔧 Better separation of concerns
- 🔧 More maintainable codebase

---

## Deprecated

- ⚠️ v1 script (`nmapai.py`) - Still functional but consider migrating
- ⚠️ Old output format - v2 uses enhanced structure
- ⚠️ Hardcoded AI provider selection - Use `--ai-provider` flag

---

## Removed

- ❌ Inline AI provider detection (now explicit)
- ❌ Some legacy CLI argument names (see migration guide)

---

## Fixed

- 🐛 Improved Unicode handling in reports
- 🐛 Better concurrent execution handling
- 🐛 More robust error recovery
- 🐛 Fixed rate limiting issues with external APIs
- 🐛 Corrected XML parsing edge cases

---

## Security

- 🔒 API keys never logged or included in reports
- 🔒 Secure credential handling
- 🔒 No sensitive data in error messages
- 🔒 Sandboxed plugin execution

---

## Performance

- ⚡ Async I/O throughout for better concurrency
- ⚡ Batch API requests where possible (EPSS)
- ⚡ Caching for repeated API calls
- ⚡ Parallel report generation
- ⚡ Optimized XML parsing

---

## Dependencies

### Added
- `aiohttp>=3.9.0` - Async HTTP client
- `pyyaml>=6.0.0` - YAML configuration support

### Updated
- `rich>=13.0.0` - Enhanced terminal UI
- `requests>=2.31.0` - HTTP client

---

## Migration Path

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions.

**Quick migration:**
```bash
# Install new dependencies
pip install -r requirements.txt

# Use v2 with same targets
python nmapai_v2.py -f targets.txt --profile standard --ai
```

---

## Known Issues

1. **Ollama Integration**: Requires manual Ollama installation
2. **NVD Rate Limits**: May be slow without API key (6 requests/minute)
3. **ExploitDB Search**: Best-effort, not all CVEs have exploits
4. **Large Scans**: Memory usage increases with many targets

---

## Upgrade Recommendations

### From v1.x to v2.0

**Immediate Benefits:**
- ✅ Multi-model AI (try Claude or Ollama)
- ✅ Vulnerability intelligence (NVD, EPSS, ExploitDB)
- ✅ Risk prioritization
- ✅ HTML dashboard

**Migration Effort:**
- Low: CLI is mostly compatible
- Medium: Some flag changes
- High: If using custom integrations

**Recommended Approach:**
1. Install v2 alongside v1
2. Test on non-production scans
3. Create custom config files
4. Migrate automation scripts
5. Remove v1 once confident

---

## Statistics

- **Lines of Code:** ~3,500+ (v1: ~700)
- **Files Created:** 25+
- **Plugins:** 9 (scanners, AI providers, enrichers)
- **New Dependencies:** 2
- **Test Coverage:** TBD
- **Documentation:** 4 comprehensive guides

---

## Credits

### v2.0 Development
- **Architecture:** sudo3rs (Riyan)
- **Plugin System:** sudo3rs (Riyan)
- **AI Integration:** sudo3rs (Riyan)
- **Enrichment Engines:** sudo3rs (Riyan)
- **Reporting System:** sudo3rs (Riyan)

### Original v1.0
- **Created by:** sudo3rs (Riyan)
- **DursVuln Integration:** Kang Ali (roomkangali)

### Special Thanks
- Nmap Project (Gordon Lyon)
- OpenAI, Anthropic, Ollama teams
- NIST NVD team
- FIRST.org EPSS project
- ExploitDB / Offensive Security
- Rich library (Will McGugan)

---

## Future Roadmap (v2.x)

### Planned Features
- [ ] Notification plugins (Slack, Discord, Email, Webhook)
- [ ] PDF report generation
- [ ] SARIF output format
- [ ] Google Gemini AI provider
- [ ] Masscan scanner plugin
- [ ] Nuclei scanner plugin
- [ ] Attack chain visualization
- [ ] Web UI for scan management
- [ ] Scheduled scanning
- [ ] Result comparison (diff between scans)
- [ ] OWASP Top 10 / CWE mapping
- [ ] MITRE ATT&CK framework integration
- [ ] Custom risk scoring profiles
- [ ] Database backend (SQLite/PostgreSQL)
- [ ] REST API server mode

### Improvements
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Better error recovery
- [ ] Retry mechanisms with exponential backoff
- [ ] Circuit breaker pattern
- [ ] Plugin hot-reloading
- [ ] Plugin marketplace

---

## Getting Started

```bash
# Quick start
pip install -r requirements.txt
python nmapai_v2.py --list-profiles
python nmapai_v2.py -f targets.txt --profile standard --ai
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

---

## Support

- **Documentation:** [README_V2.md](README_V2.md)
- **Issues:** https://github.com/Masriyan/NmapAI-gility/issues
- **Discussions:** https://github.com/Masriyan/NmapAI-gility/discussions

---

## License

MIT License - See [LICENSE](LICENSE) file.

---

**Note:** This is a major version upgrade. While we've maintained CLI compatibility where possible, please review the migration guide before upgrading production environments.

**Happy Scanning! 🎯**
