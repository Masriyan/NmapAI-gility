"""Advanced report generation with multiple formats."""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


class ReportGenerator:
    """Generate comprehensive reports in multiple formats."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def generate_all_reports(self, scan_results: Dict[str, Any], output_dir: Path):
        """Generate all configured report formats."""
        reports_generated = []

        # Always generate JSON
        json_report = await self.generate_json(scan_results, output_dir / "report.json")
        reports_generated.append(json_report)

        # Generate Markdown
        md_report = await self.generate_markdown(scan_results, output_dir / "report.md")
        reports_generated.append(md_report)

        # Generate HTML Dashboard
        html_report = await self.generate_html_dashboard(scan_results, output_dir / "dashboard.html")
        reports_generated.append(html_report)

        # Generate CSV
        csv_report = await self.generate_csv(scan_results, output_dir / "vulnerabilities.csv")
        reports_generated.append(csv_report)

        return reports_generated

    async def generate_json(self, scan_results: Dict[str, Any], output_path: Path) -> str:
        """Generate JSON report."""
        # Create serializable version
        report = {
            "scan_metadata": {
                "start_time": str(scan_results.get("start_time")),
                "end_time": str(scan_results.get("end_time")),
                "duration": scan_results.get("duration"),
                "targets_count": len(scan_results.get("targets", [])),
            },
            "hosts": scan_results.get("nmap_results", {}).get("hosts", []),
            "vulnerabilities": scan_results.get("scored_vulnerabilities", []),
            "recommendations": scan_results.get("recommendations", []),
            "ai_analysis": scan_results.get("ai_analysis"),
        }

        output_path.write_text(json.dumps(report, indent=2, default=str))
        return str(output_path)

    async def generate_markdown(self, scan_results: Dict[str, Any], output_path: Path) -> str:
        """Generate Markdown report."""
        lines = []

        # Header
        lines.append("# NmapAIGility Security Scan Report\n")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Executive Summary
        lines.append("## Executive Summary\n")
        vulns = scan_results.get("scored_vulnerabilities", [])
        critical = len([v for v in vulns if v.get("risk_level") == "critical"])
        high = len([v for v in vulns if v.get("risk_level") == "high"])
        medium = len([v for v in vulns if v.get("risk_level") == "medium"])

        lines.append(f"- **Total Vulnerabilities:** {len(vulns)}\n")
        lines.append(f"- **Critical:** {critical}\n")
        lines.append(f"- **High:** {high}\n")
        lines.append(f"- **Medium:** {medium}\n\n")

        # Hosts Discovered
        lines.append("## Hosts Discovered\n")
        hosts = scan_results.get("nmap_results", {}).get("hosts", [])
        lines.append(f"Total hosts: {len(hosts)}\n\n")

        for host in hosts[:20]:  # Limit to first 20
            lines.append(f"### {host.get('ip')} ({host.get('hostname', 'N/A')})\n")

            if host.get('os'):
                lines.append(f"**OS:** {host['os'].get('name')}\n\n")

            if host.get('ports'):
                lines.append("**Open Ports:**\n\n")
                lines.append("| Port | Protocol | Service | Version |\n")
                lines.append("|------|----------|---------|----------|\n")

                for port in host['ports'][:10]:
                    service = port.get('service', {})
                    lines.append(f"| {port['port']} | {port['protocol']} | {service.get('name', 'unknown')} | {service.get('product', '')} {service.get('version', '')} |\n")

                lines.append("\n")

        # Top Vulnerabilities
        lines.append("## Top Vulnerabilities\n")
        top_vulns = vulns[:15]

        for vuln in top_vulns:
            cve_id = vuln.get("cve_id", "UNKNOWN")
            risk_level = vuln.get("risk_level", "unknown").upper()
            priority_score = vuln.get("priority_score", 0)

            lines.append(f"### {cve_id} [{risk_level}] (Score: {priority_score:.1f})\n")

            desc = vuln.get("description", "No description available")[:200]
            lines.append(f"{desc}\n\n")

            lines.append(f"- **Host:** {vuln.get('host', 'N/A')}\n")
            lines.append(f"- **Port:** {vuln.get('port', 'N/A')}\n")
            lines.append(f"- **Service:** {vuln.get('service', 'N/A')}\n")

            if vuln.get("cvss_score"):
                lines.append(f"- **CVSS Score:** {vuln.get('cvss_score')}\n")

            if vuln.get("epss_score"):
                lines.append(f"- **EPSS (Exploit Probability):** {vuln.get('epss_score'):.2%}\n")

            if vuln.get("exploit_available"):
                lines.append(f"- **Exploit Available:** ⚠️ YES\n")

            lines.append("\n")

        # Prioritized Recommendations
        lines.append("## Prioritized Remediation Actions\n")
        recommendations = scan_results.get("recommendations", [])

        for idx, rec in enumerate(recommendations[:10], 1):
            lines.append(f"### {idx}. {rec.get('cve_id')} [{rec.get('severity').upper()}]\n")
            lines.append(f"**Priority Score:** {rec.get('score')}\n\n")
            lines.append(f"**Action:** {rec.get('action')}\n\n")
            lines.append(f"**Rationale:** {rec.get('rationale')}\n\n")

        # AI Analysis
        if scan_results.get("ai_analysis"):
            lines.append("## AI Security Analysis\n")
            lines.append(scan_results["ai_analysis"])
            lines.append("\n\n")

        output_path.write_text("".join(lines))
        return str(output_path)

    async def generate_html_dashboard(self, scan_results: Dict[str, Any], output_path: Path) -> str:
        """Generate interactive HTML dashboard."""
        vulns = scan_results.get("scored_vulnerabilities", [])
        hosts = scan_results.get("nmap_results", {}).get("hosts", [])

        critical = len([v for v in vulns if v.get("risk_level") == "critical"])
        high = len([v for v in vulns if v.get("risk_level") == "high"])
        medium = len([v for v in vulns if v.get("risk_level") == "medium"])
        low = len([v for v in vulns if v.get("risk_level") == "low"])

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NmapAIGility Security Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f1419; color: #e0e0e0; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; }}
        .header h1 {{ color: white; font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ color: #f0f0f0; font-size: 1.1em; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ background: #1a1f2e; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-left: 4px solid; }}
        .stat-card.critical {{ border-color: #f44336; }}
        .stat-card.high {{ border-color: #ff9800; }}
        .stat-card.medium {{ border-color: #ffc107; }}
        .stat-card.low {{ border-color: #4caf50; }}
        .stat-card h3 {{ font-size: 0.9em; color: #b0b0b0; text-transform: uppercase; margin-bottom: 10px; }}
        .stat-card .number {{ font-size: 3em; font-weight: bold; }}
        .section {{ background: #1a1f2e; border-radius: 12px; padding: 30px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        .section h2 {{ color: #667eea; margin-bottom: 20px; font-size: 1.8em; }}
        .vuln-item {{ background: #252b3a; padding: 20px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .vuln-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .vuln-title {{ font-size: 1.2em; font-weight: bold; color: #e0e0e0; }}
        .badge {{ padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; }}
        .badge.critical {{ background: #f44336; color: white; }}
        .badge.high {{ background: #ff9800; color: white; }}
        .badge.medium {{ background: #ffc107; color: black; }}
        .badge.low {{ background: #4caf50; color: white; }}
        .chart-container {{ max-width: 600px; margin: 0 auto; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #2a2f3e; }}
        th {{ background: #252b3a; color: #667eea; font-weight: 600; }}
        tr:hover {{ background: #252b3a; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ NmapAIGility Security Dashboard</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card critical">
                <h3>Critical</h3>
                <div class="number">{critical}</div>
            </div>
            <div class="stat-card high">
                <h3>High</h3>
                <div class="number">{high}</div>
            </div>
            <div class="stat-card medium">
                <h3>Medium</h3>
                <div class="number">{medium}</div>
            </div>
            <div class="stat-card low">
                <h3>Low / Info</h3>
                <div class="number">{low}</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Vulnerability Distribution</h2>
            <div class="chart-container">
                <canvas id="vulnChart"></canvas>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Top Vulnerabilities</h2>
'''

        # Add top vulnerabilities
        for vuln in vulns[:10]:
            cve_id = vuln.get("cve_id", "UNKNOWN")
            risk = vuln.get("risk_level", "unknown")
            score = vuln.get("priority_score", 0)
            desc = vuln.get("description", "No description available")[:150]

            html += f'''
            <div class="vuln-item">
                <div class="vuln-header">
                    <div class="vuln-title">{cve_id}</div>
                    <span class="badge {risk}">{risk.upper()}</span>
                </div>
                <p style="color: #b0b0b0; margin-bottom: 10px;">{desc}</p>
                <div style="display: flex; gap: 15px; font-size: 0.9em;">
                    <span>🎯 Priority: <strong>{score:.1f}</strong></span>
                    <span>🖥️ Host: <strong>{vuln.get('host', 'N/A')}</strong></span>
                    <span>🔌 Port: <strong>{vuln.get('port', 'N/A')}</strong></span>
                </div>
            </div>
'''

        # Add hosts section
        html += '''
        </div>

        <div class="section">
            <h2>🖥️ Discovered Hosts</h2>
            <table>
                <thead>
                    <tr>
                        <th>IP Address</th>
                        <th>Hostname</th>
                        <th>OS</th>
                        <th>Open Ports</th>
                    </tr>
                </thead>
                <tbody>
'''

        for host in hosts[:20]:
            ip = host.get('ip')
            hostname = host.get('hostname', 'N/A')
            os_name = host.get('os', {}).get('name', 'Unknown') if host.get('os') else 'Unknown'
            port_count = len(host.get('ports', []))

            html += f'''
                    <tr>
                        <td><strong>{ip}</strong></td>
                        <td>{hostname}</td>
                        <td>{os_name}</td>
                        <td>{port_count}</td>
                    </tr>
'''

        html += f'''
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('vulnChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Critical', 'High', 'Medium', 'Low/Info'],
                datasets: [{{
                    data: [{critical}, {high}, {medium}, {low}],
                    backgroundColor: ['#f44336', '#ff9800', '#ffc107', '#4caf50'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ color: '#e0e0e0', font: {{ size: 14 }} }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
'''

        output_path.write_text(html)
        return str(output_path)

    async def generate_csv(self, scan_results: Dict[str, Any], output_path: Path) -> str:
        """Generate CSV report of vulnerabilities."""
        import csv

        vulns = scan_results.get("scored_vulnerabilities", [])

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['CVE_ID', 'Severity', 'Priority_Score', 'Host', 'Port', 'Service', 'CVSS_Score', 'EPSS_Score', 'Exploit_Available'])

            for vuln in vulns:
                writer.writerow([
                    vuln.get('cve_id', ''),
                    vuln.get('risk_level', ''),
                    f"{vuln.get('priority_score', 0):.2f}",
                    vuln.get('host', ''),
                    vuln.get('port', ''),
                    vuln.get('service', ''),
                    vuln.get('cvss_score', ''),
                    f"{vuln.get('epss_score', 0):.4f}",
                    'Yes' if vuln.get('exploit_available') else 'No',
                ])

        return str(output_path)
