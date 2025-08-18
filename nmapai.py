#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NmapAI-gility — Python Edition
Author: sudo3rs (Riyan) | DursVuln: Kang Ali | License: MIT

Features
- Animated progress UI (rich) for:
  * Nmap (live % via --stats-every parsing)
  * Nikto (per-target progress)
  * AI analysis (per-chunk progress)
- Nmap outputs: .nmap, .gnmap, .xml + CSV/JSON/MD summaries
- DursVuln integration:
  * --dursvuln to enable
  * --dursvuln-global to use global --script=dursvuln
  * --dursvuln-script PATH to local dursvuln.nse
  * --dursvuln-db PATH (cve-main.json)
  * --dursvuln-update (download cve-main.json if missing)
  * --dursvuln-min {LOW,MEDIUM,HIGH,CRITICAL}
  * --dursvuln-output {concise,full}
- Nikto runs only against detected HTTP(S) services (concurrent)
- Optional AI analysis using OpenAI-compatible Chat Completions API
- Unicode dash normalization (–, —) -> "--"
- Dry run (-r) and debug (-d) modes
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional

# Soft dependencies
try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    RICH = True
except Exception:
    RICH = False

try:
    import requests
except Exception:
    requests = None  # will guard when needed

CONSOLE = Console(force_terminal=True) if RICH else None

DURSVULN_DB_RAW_URL = "https://raw.githubusercontent.com/roomkangali/DursVuln-Database/main/cve-main.json"


# ---------------------- Utils ----------------------
def ts() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def log_path(out_dir: Path) -> Path:
    return out_dir / "nmap_scan.log"


def log_write(out_dir: Path, msg: str) -> None:
    line = f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n"
    with open(log_path(out_dir), "a", encoding="utf-8", errors="ignore") as f:
        f.write(line)


def which(cmd: str) -> Optional[str]:
    from shutil import which as _which
    return _which(cmd)


def normalize_dashes(s: str) -> str:
    return s.replace("—", "--").replace("–", "--")


def ensure_cmd(cmd: str, hint: str = "") -> None:
    if which(cmd) is None:
        raise SystemExit(f"[!] Missing dependency: {cmd}. {hint}")


def write_file(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", errors="ignore") as f:
        f.write(content)


def read_nonempty_lines(path: Path) -> List[str]:
    lines: List[str] = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            lines.append(s)
    return lines


# ---------------------- Nmap Runner ----------------------
class NmapRunner:
    def __init__(
        self,
        targets_file: Path,
        out_dir: Path,
        nmap_params: str,
        enable_durs: bool,
        use_global_script: bool,
        durs_script: Optional[Path],
        durs_db: Optional[Path],
        durs_min: Optional[str],
        durs_output: str,
        dry_run: bool,
    ):
        self.targets_file = targets_file
        self.out_dir = out_dir
        self.nmap_params = normalize_dashes(nmap_params or "")
        self.enable_durs = enable_durs
        self.use_global_script = use_global_script
        self.durs_script = durs_script
        self.durs_db = durs_db
        self.durs_min = durs_min
        self.durs_output = durs_output
        self.dry_run = dry_run

        self.out_normal = out_dir / "nmap_results.nmap"
        self.out_grep = out_dir / "nmap_results.gnmap"
        self.out_xml = out_dir / "nmap_results.xml"

    def build_cmd(self) -> List[str]:
        base = ["nmap", "-iL", str(self.targets_file)]
        # parse params like a shell would
        extra = shlex.split(self.nmap_params)
        base += extra
        # progress + outputs
        base += ["--stats-every", "2s", "-oN", str(self.out_normal), "-oG", str(self.out_grep), "-oX", str(self.out_xml), "-v"]
        # dursvuln integration
        if self.enable_durs:
            if self.use_global_script:
                base += ["--script", "dursvuln"]
            else:
                if not self.durs_script or not self.durs_script.exists():
                    raise SystemExit("[!] DursVuln enabled but NSE script not found. Use --dursvuln-global or --dursvuln-script PATH")
                base += ["--script", str(self.durs_script)]
            args = []
            if self.durs_db:
                args.append(f"db_path={self.durs_db}")
            if self.durs_min:
                args.append(f"min_severity={self.durs_min}")
            if self.durs_output:
                args.append(f"dursvuln.output={self.durs_output}")
            if args:
                base += ["--script-args", ",".join(args)]
        return base

    async def run(self, total_targets: int) -> int:
        cmd = self.build_cmd()
        log_write(self.out_dir, f"Nmap argv: {' '.join(map(shlex.quote, cmd))}")

        if self.dry_run:
            msg = f"[dry-run] would run: {' '.join(map(shlex.quote, cmd))}"
            if RICH:
                CONSOLE.print(Panel(msg, title="Nmap", border_style="cyan"))
            else:
                print(msg)
            return 0

        prog_re = re.compile(r"About\s+([0-9]+(?:\.[0-9]+)?)%\s+done")
        etc_re = re.compile(r"ETC:\s*([^\r\n]+)")

        if RICH:
            CONSOLE.print(Panel(f"[bold cyan]Scanning {total_targets} target(s)[/bold cyan]\n[dim]Output → {self.out_dir}[/dim]\n[dim]Params → {self.nmap_params}[/dim]", title="Nmap", border_style="cyan"))

            bar = Progress(
                SpinnerColumn(),
                TextColumn("[bold]Nmap[/bold]"),
                BarColumn(bar_width=None),
                TextColumn("{task.percentage:>6.2f}%"),
                TextColumn("{task.fields[etc]}"),
                TimeRemainingColumn(),
                transient=False,
                console=CONSOLE,
            )
            task = bar.add_task("nmap", total=100.0, etc="")
            with bar:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                async def reader(stream, to_log=True):
                    nonlocal task
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        s = line.decode(errors="ignore")
                        if to_log:
                            log_write(self.out_dir, s.rstrip("\n"))
                        m = prog_re.search(s)
                        if m:
                            pct = float(m.group(1))
                            bar.update(task, completed=pct)
                        m2 = etc_re.search(s)
                        if m2:
                            bar.update(task, etc=f"[dim]{m2.group(1)}[/dim]")
                await asyncio.gather(reader(proc.stdout, to_log=True), reader(proc.stderr, to_log=True))
                rc = await proc.wait()
                if rc == 0:
                    bar.update(task, completed=100.0, etc="[green]Done[/green]")
                return rc
        else:
            print(f"[Nmap] Running: {' '.join(map(shlex.quote, cmd))}")
            proc = await asyncio.create_subprocess_exec(*cmd)
            rc = await proc.wait()
            return rc


# ---------------------- Summaries ----------------------
def summarize_gnmap(gnmap: Path, out_dir: Path) -> Tuple[Path, Path, Path]:
    csv_path = out_dir / "nmap_summary.csv"
    json_path = out_dir / "nmap_summary.json"
    md_path = out_dir / "nmap_summary.md"

    if not gnmap.exists() or gnmap.stat().st_size == 0:
        return csv_path, json_path, md_path

    rows: List[Tuple[str, str, str, str]] = []
    with open(gnmap, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "Host: " in line and "Ports: " in line:
                parts = line.strip()
                host = parts.split()[1]
                ports_str = re.sub(r"^.*Ports:\s*", "", parts)
                for seg in ports_str.split(","):
                    seg = seg.strip()
                    if "open" in seg:
                        bits = seg.split("/")
                        if len(bits) >= 5:
                            port = bits[0]
                            state = bits[1]
                            proto = bits[2]
                            svc = bits[4] or "-"
                            if state == "open":
                                rows.append((host, port, proto, svc))

    # CSV
    rows = sorted(set(rows))
    with open(csv_path, "w", newline="", encoding="utf-8", errors="ignore") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)

    # JSON
    with open(json_path, "w", encoding="utf-8", errors="ignore") as f:
        json.dump(
            [{"host": h, "port": p, "proto": pr, "service": s} for (h, p, pr, s) in rows],
            f,
            indent=2,
        )

    # MD
    buf = []
    buf.append("# Nmap Summary\n")
    buf.append(f"- Generated: {dt.datetime.now().isoformat()}\n")
    buf.append(f"- Source: `nmap_results.gnmap`\n\n")
    if not rows:
        buf.append("_No open ports found._\n")
    else:
        # Group by host
        from collections import defaultdict
        g = defaultdict(list)
        for r in rows:
            g[r[0]].append(r)
        for host, items in g.items():
            buf.append(f"## {host}\n\n")
            buf.append("| Port | Proto | Service |\n|------|-------|---------|\n")
            for _, port, proto, svc in items:
                buf.append(f"| {port} | {proto} | {svc} |\n")
            buf.append("\n")
    write_file(md_path, "".join(buf))

    return csv_path, json_path, md_path


# ---------------------- Nikto Runner ----------------------
class NiktoRunner:
    def __init__(self, csv_summary: Path, out_dir: Path, concurrency: int, dry_run: bool):
        self.csv_summary = csv_summary
        self.out_dir = out_dir / "nikto"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.concurrency = max(1, int(concurrency))
        self.dry_run = dry_run
        self.targets: List[Tuple[str, str, str]] = []  # (host, port, svc)

    def _detect_targets(self) -> None:
        if not self.csv_summary.exists() or self.csv_summary.stat().st_size == 0:
            return
        with open(self.csv_summary, "r", encoding="utf-8", errors="ignore") as f:
            for row in csv.reader(f):
                if len(row) < 4:
                    continue
                host, port, _proto, svc = row[0], row[1], row[2], row[3].lower()
                if "http" in svc or port in {"80", "443", "8080", "8000", "8001", "8888", "8443", "5000"}:
                    self.targets.append((host, port, svc))
        # dedupe
        self.targets = sorted(set(self.targets))

    async def _run_one(self, sem: asyncio.Semaphore, host: str, port: str, svc: str, progress_task=None):
        async with sem:
            scheme = "https" if port in {"443", "8443"} or "https" in svc or "ssl" in svc else "http"
            out_file = self.out_dir / f"{host}_{port}.htm"
            cmd = ["nikto", "-h", f"{scheme}://{host}:{port}", "-o", str(out_file), "-Format", "htm"]
            log_write(self.out_dir.parent, f"Nikto argv: {' '.join(map(shlex.quote, cmd))}")

            if self.dry_run:
                if RICH:
                    CONSOLE.print(f"[yellow][dry-run][/yellow] nikto {' '.join(map(shlex.quote, cmd))}")
                else:
                    print("[dry-run]", " ".join(map(shlex.quote, cmd)))
                if progress_task:
                    progress_task.advance(1)
                return

            try:
                proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await proc.communicate()
            except FileNotFoundError:
                raise SystemExit("[!] Nikto not found in PATH. Install Nikto or use -K/--no-nikto.")
            finally:
                if progress_task:
                    progress_task.advance(1)

    async def run(self):
        self._detect_targets()
        total = len(self.targets)
        if total == 0:
            if RICH:
                CONSOLE.print("[yellow]No HTTP(S) services detected; skipping Nikto.[/yellow]")
            else:
                print("No HTTP(S) services detected; skipping Nikto.")
            return

        if RICH:
            bar = Progress(
                SpinnerColumn(),
                TextColumn("[bold]Nikto[/bold]"),
                BarColumn(bar_width=None),
                TextColumn("{task.completed}/{task.total}"),
                TimeRemainingColumn(),
                transient=False,
                console=CONSOLE,
            )
            task = bar.add_task("nikto", total=total)
            with bar:
                sem = asyncio.Semaphore(self.concurrency)
                await asyncio.gather(*(self._run_one(sem, h, p, s, progress_task=bar.tasks[0]) for (h, p, s) in self.targets))
        else:
            print(f"[Nikto] {total} target(s), concurrency={self.concurrency}")
            sem = asyncio.Semaphore(self.concurrency)
            await asyncio.gather(*(self._run_one(sem, h, p, s) for (h, p, s) in self.targets))


# ---------------------- DursVuln helpers ----------------------
def maybe_update_durs_db(out_dir: Path, durs_db: Optional[Path], do_update: bool) -> Path | None:
    if not do_update:
        return durs_db if durs_db and durs_db.exists() else durs_db

    # Prefer requests; fallback to urllib
    dest = durs_db if durs_db else (out_dir / "dursvuln-db" / "cve-main.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        if requests:
            r = requests.get(DURSVULN_DB_RAW_URL, timeout=60)
            r.raise_for_status()
            write_file(dest, r.text)
        else:
            import urllib.request
            with urllib.request.urlopen(DURSVULN_DB_RAW_URL, timeout=60) as resp:
                data = resp.read().decode("utf-8", "ignore")
                write_file(dest, data)
        if RICH:
            CONSOLE.print(f"[green]DursVuln DB downloaded → {dest}[/green]")
        else:
            print("DursVuln DB downloaded:", dest)
        return dest
    except Exception as e:
        if RICH:
            CONSOLE.print(f"[yellow]Failed to refresh DursVuln DB: {e}[/yellow]")
        else:
            print("Failed to refresh DursVuln DB:", e)
        return durs_db


# ---------------------- DursVuln output extraction ----------------------
def extract_dursvuln_blocks(nmap_normal: Path, out_dir: Path) -> Path:
    out = out_dir / "dursvuln_summary.md"
    if not nmap_normal.exists() or nmap_normal.stat().st_size == 0:
        return out
    content = nmap_normal.read_text(encoding="utf-8", errors="ignore").splitlines()
    buf = ["# DursVuln Findings\n", f"\n_Generated: {dt.datetime.now().isoformat()}_\n\n"]
    inblock = False
    saw_any = False
    host_hdr = None

    for line in content:
        if line.startswith("Nmap scan report for"):
            host_hdr = line
        if re.search(r"dursvuln", line, flags=re.I):
            saw_any = True
            if host_hdr:
                buf.append(f"## {host_hdr}\n\n")
                host_hdr = None
            buf.append("```\n")
            buf.append(line + "\n")
            inblock = True
            continue
        if inblock:
            if not line.strip() or line.startswith("Nmap scan report for"):
                buf.append("```\n\n")
                inblock = False
                if line.startswith("Nmap scan report for"):
                    host_hdr = line
            elif re.match(r"^\s", line) or line.startswith("|"):
                buf.append(line + "\n")
            else:
                buf.append("```\n\n")
                inblock = False

    if inblock:
        buf.append("```\n\n")
    if not saw_any:
        buf = ["_No DursVuln script output detected in normal report._\n"]
    write_file(out, "".join(buf))
    return out


# ---------------------- AI Analysis ----------------------
async def ai_analyze(out_dir: Path, model: str, endpoint: str, max_tokens: int, temperature: float, top_p: float) -> Optional[Path]:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        if RICH:
            CONSOLE.print("[yellow]AI skipped: OPENAI_API_KEY not set.[/yellow]")
        else:
            print("AI skipped: OPENAI_API_KEY not set.")
        return None

    corpus = out_dir / "analysis_corpus.txt"
    parts = []
    with open(corpus, "w", encoding="utf-8", errors="ignore") as f:
        f.write("=== NMAP (.nmap) ===\n")
        try:
            f.write((out_dir / "nmap_results.nmap").read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass
        ds = out_dir / "dursvuln_summary.md"
        if ds.exists():
            f.write("\n\n=== DursVuln Summary ===\n")
            f.write(ds.read_text(encoding="utf-8", errors="ignore"))

    CHUNK = 14000
    blob = corpus.read_text(encoding="utf-8", errors="ignore")
    for i in range(0, len(blob), CHUNK):
        parts.append(blob[i : i + CHUNK])

    if not parts:
        return None

    out = out_dir / "ai_analysis.md"
    write_file(out, f"# AI Analysis\n\n_Model: {model}; Generated: {dt.datetime.now().isoformat()}_\n\n")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    async def one_chunk(idx: int, payload: dict) -> str:
        # Use requests in a thread (simpler than aiohttp to avoid new deps)
        import functools
        loop = asyncio.get_running_loop()
        def _post():
            if requests is None:
                raise RuntimeError("requests not installed")
            return requests.post(endpoint, headers=headers, json=payload, timeout=90)
        resp = await loop.run_in_executor(None, _post)
        if resp.status_code == 200:
            try:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception:
                return f"_Chunk {idx} parse error_"
        else:
            return f"_Chunk {idx} error {resp.status_code}: {resp.text[:500]}_"

    if RICH:
        bar = Progress(
            SpinnerColumn(),
            TextColumn("[bold]AI[/bold]"),
            BarColumn(bar_width=None),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            transient=False,
            console=CONSOLE,
        )
        task = bar.add_task("ai", total=len(parts))
        with bar:
            for i, chunk in enumerate(parts, 1):
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a security analyst. Analyze Nmap and DursVuln findings. Summarize key risks, candidate CVEs, and top 5 prioritized actions. Concise Markdown."},
                        {"role": "user", "content": f"Analyze these scan results:\n\n{chunk}"},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                }
                content = await one_chunk(i, payload)
                with open(out, "a", encoding="utf-8", errors="ignore") as f:
                    f.write(f"## Chunk {i}\n\n{content}\n\n")
                bar.update(task, advance=1)
    else:
        print(f"[AI] {len(parts)} chunk(s)")
        for i, chunk in enumerate(parts, 1):
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a security analyst. Analyze Nmap and DursVuln findings. Summarize key risks, candidate CVEs, and top 5 prioritized actions. Concise Markdown."},
                    {"role": "user", "content": f"Analyze these scan results:\n\n{chunk}"},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }
            content = await one_chunk(i, payload)
            with open(out, "a", encoding="utf-8", errors="ignore") as f:
                f.write(f"## Chunk {i}\n\n{content}\n\n")

    if RICH:
        CONSOLE.print(f"[green]AI analysis → {out.name}[/green]")
    else:
        print("AI analysis:", out)
    return out


# ---------------------- CLI ----------------------
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="NmapAI-gility — Python Edition")
    p.add_argument("-f", "--file", required=True, type=Path, help="IP/host/CIDR list file")
    p.add_argument("-n", "--nmap", required=True, help='Nmap parameters, e.g. "-sV -T4 --top-ports 200"')
    p.add_argument("-o", "--out-dir", type=Path, default=None, help="Output directory (default: ./out_nmapai_<ts>)")
    p.add_argument("-t", "--threads", type=int, default=2, help="Nikto parallel threads (default: 2)")
    p.add_argument("-K", "--no-nikto", action="store_true", help="Disable Nikto stage")
    p.add_argument("-a", "--ai", action="store_true", help="Enable AI analysis (requires OPENAI_API_KEY)")
    p.add_argument("-m", "--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), help="AI model (default: env OPENAI_MODEL or gpt-4o-mini)")
    p.add_argument("--ai-endpoint", default=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1/chat/completions"), help="AI endpoint URL")
    p.add_argument("--ai-max-tokens", type=int, default=700)
    p.add_argument("--ai-temp", type=float, default=0.2)
    p.add_argument("--ai-top-p", type=float, default=1.0)
    # DursVuln
    p.add_argument("-D", "--dursvuln", action="store_true", help="Enable DursVuln NSE")
    p.add_argument("-G", "--dursvuln-global", action="store_true", help="Use global --script=dursvuln")
    p.add_argument("-L", "--dursvuln-script", type=Path, help="Path to local dursvuln.nse")
    p.add_argument("-P", "--dursvuln-db", type=Path, help="Path to cve-main.json")
    p.add_argument("-S", "--dursvuln-min", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], help="Min severity")
    p.add_argument("-O", "--dursvuln-output", choices=["concise", "full"], default="concise")
    p.add_argument("-U", "--dursvuln-update", action="store_true", help="Download/refresh cve-main.json if needed")
    # Modes
    p.add_argument("-r", "--dry-run", action="store_true", help="Dry run (print actions only)")
    p.add_argument("-d", "--debug", action="store_true", help="Debug mode (verbose)")
    return p


async def main_async(args: argparse.Namespace) -> None:
    # deps
    ensure_cmd("nmap", "Install Nmap from https://nmap.org/download.html")
    if not args.no_nikto:
        if which("nikto") is None:
            # degrade gracefully
            if RICH:
                CONSOLE.print("[yellow]Nikto not found; the Nikto stage will be skipped.[/yellow]")
            else:
                print("Nikto not found; skipping Nikto stage.")
            args.no_nikto = True

    # out dir + log
    out_dir = args.out_dir or Path(f"out_nmapai_{ts()}")
    out_dir.mkdir(parents=True, exist_ok=True)
    log_write(out_dir, f"Args: {vars(args)}")

    # sanitize targets
    if not args.file.exists():
        raise SystemExit(f"[!] Targets file not found: {args.file}")
    sanitized = out_dir / "targets_clean.txt"
    targets = read_nonempty_lines(args.file)
    if not targets:
        raise SystemExit("[!] No valid targets in file.")
    write_file(sanitized, "\n".join(targets) + "\n")
    if RICH:
        CONSOLE.print(f"[green]Targets sanitized → {sanitized} ({len(targets)} host(s))[/green]")
    else:
        print("Targets sanitized:", sanitized, len(targets), "host(s)")

    # DursVuln DB update (optional)
    durs_db = maybe_update_durs_db(out_dir, args.dursvuln_db, args.dursvuln_update) if args.dursvuln else args.dursvuln_db

    # Nmap
    nmap = NmapRunner(
        targets_file=sanitized,
        out_dir=out_dir,
        nmap_params=args.nmap,
        enable_durs=args.dursvuln,
        use_global_script=args.dursvuln_global,
        durs_script=args.dursvuln_script,
        durs_db=durs_db,
        durs_min=args.dursvuln_min,
        durs_output=args.dursvuln_output,
        dry_run=args.dry_run,
    )
    rc = await nmap.run(total_targets=len(targets))
    if rc != 0:
        raise SystemExit(f"[!] Nmap failed with exit code {rc}")

    # Summaries
    csv_path, json_path, md_path = summarize_gnmap(nmap.out_grep, out_dir)
    if RICH:
        t = Table(title="Summary Files", show_edge=False)
        t.add_column("File"); t.add_column("Path")
        t.add_row("CSV", str(csv_path))
        t.add_row("JSON", str(json_path))
        t.add_row("Markdown", str(md_path))
        CONSOLE.print(t)
    else:
        print("Summaries:", csv_path, json_path, md_path)

    # Nikto
    if not args.no_nikto and not args.dry_run:
        nikto = NiktoRunner(csv_summary=csv_path, out_dir=out_dir, concurrency=args.threads, dry_run=False)
        await nikto.run()

    # DursVuln extraction
    if args.dursvuln and not args.dry_run:
        durs_md = extract_dursvuln_blocks(nmap.out_normal, out_dir)
        if RICH:
            CONSOLE.print(f"[green]DursVuln summary → {durs_md.name}[/green]")
        else:
            print("DursVuln summary:", durs_md)

    # AI analysis
    if args.ai and not args.dry_run:
        await ai_analyze(
            out_dir=out_dir,
            model=args.model,
            endpoint=args.ai_endpoint,
            max_tokens=args.ai_max_tokens,
            temperature=args.ai_temp,
            top_p=args.ai_top_p,
        )

    # Wrap-up
    if RICH:
        CONSOLE.rule("[bold blue]All done[/bold blue]")
        files = [
            ("Nmap", "nmap_results.nmap | .gnmap | .xml"),
            ("Summaries", f"{csv_path.name} | {json_path.name} | {md_path.name}"),
            ("DursVuln", "dursvuln_summary.md" if args.dursvuln else "-"),
            ("Nikto", "nikto/" if not args.no_nikto else "-"),
            ("Logs", log_path(out_dir).name),
            ("AI", "ai_analysis.md" if args.ai else "-"),
        ]
        tb = Table(show_edge=False)
        tb.add_column("Item", style="bold")
        tb.add_column("Value")
        for k, v in files:
            tb.add_row(k, v)
        CONSOLE.print(tb)
        CONSOLE.print(f"[bold]Output folder:[/bold] {out_dir}")
    else:
        print("All done. Output folder:", out_dir)


def main():
    args = build_arg_parser().parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        if RICH:
            CONSOLE.print("[red]Interrupted by user.[/red]")
        else:
            print("Interrupted by user.")


if __name__ == "__main__":
    main()
