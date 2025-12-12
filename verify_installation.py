#!/usr/bin/env python3
"""
Verification script for NmapAIGility v2.0 installation.
Run this to check if all dependencies and components are properly installed.
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)


def check_python_version():
    """Check Python version."""
    print("\n[*] Checking Python version...")
    version = sys.version_info
    if version >= (3, 9):
        print(f"    ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"    ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False


def check_dependencies():
    """Check Python dependencies."""
    print("\n[*] Checking Python dependencies...")

    deps = {
        'rich': 'rich',
        'aiohttp': 'aiohttp',
        'requests': 'requests',
        'yaml': 'pyyaml',
    }

    all_ok = True
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"    ✓ {package}")
        except ImportError:
            print(f"    ✗ {package} (Run: pip install {package})")
            all_ok = False

    return all_ok


def check_system_tools():
    """Check system tools."""
    print("\n[*] Checking system tools...")

    tools = ['nmap', 'nikto']
    all_ok = True

    for tool in tools:
        try:
            result = subprocess.run(
                ['which', tool],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                print(f"    ✓ {tool} ({path})")
            else:
                print(f"    ⚠ {tool} (Not found - optional)")
                if tool == 'nmap':
                    all_ok = False
        except Exception as e:
            print(f"    ✗ {tool} (Error: {e})")
            if tool == 'nmap':
                all_ok = False

    return all_ok


def check_files():
    """Check if all required files exist."""
    print("\n[*] Checking project files...")

    required_files = [
        'nmapai_v2.py',
        'requirements.txt',
        'setup.py',
        'nmapai/__init__.py',
        'nmapai/core/scanner_manager.py',
        'nmapai/plugins/scanners/nmap_scanner.py',
        'nmapai/plugins/ai_providers/openai_provider.py',
        'nmapai/plugins/enrichers/nvd_enricher.py',
    ]

    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"    ✓ {file}")
        else:
            print(f"    ✗ {file} (Missing)")
            all_ok = False

    return all_ok


def check_structure():
    """Check directory structure."""
    print("\n[*] Checking directory structure...")

    required_dirs = [
        'nmapai',
        'nmapai/core',
        'nmapai/plugins',
        'nmapai/plugins/scanners',
        'nmapai/plugins/ai_providers',
        'nmapai/plugins/enrichers',
        'nmapai/utils',
        'nmapai/config',
    ]

    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.is_dir():
            print(f"    ✓ {dir_path}/")
        else:
            print(f"    ✗ {dir_path}/ (Missing)")
            all_ok = False

    return all_ok


def check_env_vars():
    """Check environment variables."""
    print("\n[*] Checking environment variables...")
    import os

    env_vars = {
        'OPENAI_API_KEY': 'OpenAI API key',
        'ANTHROPIC_API_KEY': 'Anthropic API key (optional)',
        'NVD_API_KEY': 'NVD API key (optional)',
    }

    found_any = False
    for var, desc in env_vars.items():
        value = os.environ.get(var)
        if value:
            masked = value[:8] + '...' if len(value) > 8 else '***'
            print(f"    ✓ {var} ({masked})")
            found_any = True
        else:
            if var == 'OPENAI_API_KEY':
                print(f"    ⚠ {var} (Not set - required for AI features)")
            else:
                print(f"    ⚠ {var} (Not set - {desc})")

    if not found_any:
        print("    ⚠ No API keys configured (AI features will be disabled)")

    return True  # Don't fail on missing env vars


def test_import():
    """Test importing main modules."""
    print("\n[*] Testing module imports...")

    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))

        print("    [*] Importing nmapai...")
        import nmapai
        print(f"        ✓ nmapai v{nmapai.__version__}")

        print("    [*] Importing core modules...")
        from nmapai.core.scanner_manager import ScannerManager
        print("        ✓ ScannerManager")

        from nmapai.core.vulnerability_engine import VulnerabilityEngine
        print("        ✓ VulnerabilityEngine")

        from nmapai.core.report_generator import ReportGenerator
        print("        ✓ ReportGenerator")

        print("    [*] Importing plugins...")
        from nmapai.plugins.scanners.nmap_scanner import NmapScanner
        print("        ✓ NmapScanner")

        from nmapai.plugins.ai_providers.openai_provider import OpenAIProvider
        print("        ✓ OpenAIProvider")

        from nmapai.plugins.enrichers.nvd_enricher import NVDEnricher
        print("        ✓ NVDEnricher")

        print("    [*] All imports successful!")
        return True

    except ImportError as e:
        print(f"    ✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"    ✗ Unexpected error: {e}")
        return False


def main():
    """Main verification routine."""
    print_header("NmapAIGility v2.0 - Installation Verification")

    results = {}

    # Run all checks
    results['Python Version'] = check_python_version()
    results['Dependencies'] = check_dependencies()
    results['System Tools'] = check_system_tools()
    results['Project Files'] = check_files()
    results['Directory Structure'] = check_structure()
    results['Environment Variables'] = check_env_vars()
    results['Module Imports'] = test_import()

    # Summary
    print_header("Verification Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print()
    for check, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:10} {check}")

    print(f"\n  Result: {passed}/{total} checks passed")

    if passed == total:
        print("\n  🎉 Installation verified successfully!")
        print("\n  Next steps:")
        print("    1. Set API keys: export OPENAI_API_KEY='sk-...'")
        print("    2. Create targets: echo 'scanme.nmap.org' > targets.txt")
        print("    3. Run scan: python nmapai_v2.py -f targets.txt --profile standard --ai")
        print()
        return 0
    else:
        print("\n  ⚠ Some checks failed. Please fix the issues above.")
        print("\n  Common fixes:")
        print("    - Install dependencies: pip install -r requirements.txt")
        print("    - Install Nmap: sudo apt-get install nmap")
        print("    - Set API key: export OPENAI_API_KEY='sk-...'")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
