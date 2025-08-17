#!/usr/bin/env bash
# nmapai_gility.sh — Nmap + (optional) DursVulnNSE + (optional) Nikto + (optional) AI
# Author: sudo3rs
# DursVuln :Kang Ali 
# License: MIT
#
# 2025-08 Revamp:
# - Strong error handling, debug (-d), dry run (-r)
# - Timestamped output dir, unified logging
# - Nmap normal/grepable/XML outputs + CSV/JSON/MD summaries
# - Nikto only for discovered HTTP(S), parallel (-t)
# - AI analysis (chunking, retries) via $OPENAI_API_KEY (no hardcoded keys)
# - DursVuln integration:
#     * -D enable, -G use global --script=dursvuln, or -L path/to/dursvuln.nse
#     * -P path/to/cve-main.json or -U to auto-update/fetch from DB repo
#     * -S min severity (LOW|MEDIUM|HIGH|CRITICAL), -O output mode (concise|full)
#     * Extract DursVuln findings into dursvuln_summary.md
#
# Usage (quick):
#   ./nmapai_gility.sh -f targets.txt -n "-sV -T4 --top-ports 2000" -D -G -U -S HIGH -O concise
#
# ENV:
#   OPENAI_API_KEY=sk-xxxx               (for -a AI analysis)
#   OPENAI_MODEL=gpt-4o-mini             (default fallback if unset)

set -Eeuo pipefail
IFS=$'\n\t'

# ---------- Colors ----------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

# ---------- Defaults ----------
IP_LIST_FILE=""
NMAP_PARAMETERS=""
OUT_DIR=""
RESULTS_BASENAME="nmap_results"
LOG_FILE=""
DRY_RUN="false"
DEBUG_MODE="false"

# Nikto
ENABLE_NIKTO="true"
NIKTO_CONCURRENCY=2

# AI
ENABLE_AI="false"
AI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}"
AI_MAX_TOKENS="700"
AI_TEMPERATURE="0.2"
AI_TOP_P="1"
AI_ENDPOINT="${OPENAI_ENDPOINT:-https://api.openai.com/v1/chat/completions}"

# DursVuln NSE + DB
ENABLE_DURSVULN="false"
DURSVULN_USE_GLOBAL="false"     # use --script=dursvuln
DURSVULN_SCRIPT_PATH=""         # local ./dursvuln.nse or custom path
DURSVULN_DB_PATH=""             # path to cve-main.json
DURSVULN_MIN_SEVERITY=""        # LOW|MEDIUM|HIGH|CRITICAL
DURSVULN_OUTPUT="concise"       # concise|full
DURSVULN_UPDATE_DB="false"      # auto fetch/update cve-main.json
DURSVULN_DB_RAW_URL="https://raw.githubusercontent.com/roomkangali/DursVuln-Database/main/cve-main.json"

SPIN_DELAY="0.2"

# ---------- Helpers ----------
die()  { echo -e "${RED}ERROR:${NC} $*" >&2; exit 1; }
note() { echo -e "${CYAN}[*]${NC} $*"; }
ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
log()  { echo "[$(date +'%F %T')] $*" | tee -a "$LOG_FILE" >/dev/null; }
ts()   { date +'%Y%m%d_%H%M%S'; }

require_cmd() { for c in "$@"; do command -v "$c" >/dev/null 2>&1 || die "Missing dependency: $c"; done }
optional_cmd() { command -v "$1" >/dev/null 2>&1; }

spinner() {
  local pid=$1 spin='-\|/' i=0
  while kill -0 "$pid" >/dev/null 2>&1; do
    printf "\r${CYAN}Working... %s${NC}" "${spin:i++%${#spin}:1}"
    sleep "$SPIN_DELAY"
  done
  printf "\r${GREEN}Done!        ${NC}\n"
}

cleanup() {
  local code=$?
  if [[ $code -ne 0 ]]; then
    echo -e "${RED}Script terminated with errors (exit ${code}). See log: ${LOG_FILE}${NC}"
  fi
}
trap cleanup EXIT

usage() {
  cat <<EOF
Usage:
  $0 -f <ip_list_file> -n "<nmap_parameters>" [options]

Options:
  -f FILE      IP/host/CIDR list file
  -n PARAMS    Nmap parameters (quoted)
  -o DIR       Output directory (default: ./out_nmapai_<timestamp>)
  -t NUM       Nikto parallel threads (default: ${NIKTO_CONCURRENCY})
  -K           Disable Nikto
  -a           Enable AI analysis (requires OPENAI_API_KEY)
  -m MODEL     AI model (default: ${AI_MODEL})
  -D           Enable DursVulnNSE integration
  -G           Use globally installed NSE (--script=dursvuln)
  -L PATH      Path to local dursvuln.nse (if not global)
  -P PATH      Path to DursVuln DB cve-main.json (else auto-detect)
  -S LEVEL     DursVuln min severity: LOW|MEDIUM|HIGH|CRITICAL
  -O MODE      DursVuln output mode: concise|full (default: concise)
  -U           Update/fetch DursVuln DB (download cve-main.json if needed)
  -d           Debug mode (set -x)
  -r           Dry run (print commands only)
  -h           Help

Backward-compatible:
  $0 <ip_list_file> "<nmap_parameters>"
EOF
}

# ---------- Parse args (support positional) ----------
if [[ $# -ge 2 && $1 != -* ]]; then
  IP_LIST_FILE="$1"; shift
  NMAP_PARAMETERS="$*"
else
  while getopts ":f:n:o:t:Kam:drhDGL:P:S:O:U" opt; do
    case "$opt" in
      f) IP_LIST_FILE="$OPTARG" ;;
      n) NMAP_PARAMETERS="$OPTARG" ;;
      o) OUT_DIR="$OPTARG" ;;
      t) NIKTO_CONCURRENCY="$OPTARG" ;;
      K) ENABLE_NIKTO="false" ;;
      a) ENABLE_AI="true" ;;
      m) AI_MODEL="$OPTARG" ;;
      D) ENABLE_DURSVULN="true" ;;
      G) DURSVULN_USE_GLOBAL="true" ;;
      L) DURSVULN_SCRIPT_PATH="$OPTARG" ;;
      P) DURSVULN_DB_PATH="$OPTARG" ;;
      S) DURSVULN_MIN_SEVERITY="$OPTARG" ;;
      O) DURSVULN_OUTPUT="$OPTARG" ;;
      U) DURSVULN_UPDATE_DB="true" ;;
      d) DEBUG_MODE="true" ;;
      r) DRY_RUN="true" ;;
      h) usage; exit 0 ;;
      \?) usage; die "Unknown option: -$OPTARG" ;;
      :)  usage; die "Option -$OPTARG requires an argument." ;;
    esac
  done
fi

[[ -z "$IP_LIST_FILE" ]]    && { usage; die "Missing -f <ip_list_file>."; }
[[ -z "$NMAP_PARAMETERS" ]] && { usage; die "Missing -n \"<nmap_parameters>\"."; }
[[ ! -r "$IP_LIST_FILE" ]]  && die "Cannot read IP list file: $IP_LIST_FILE"

[[ "$DEBUG_MODE" == "true" ]] && set -x

if [[ -z "${OUT_DIR:-}" ]]; then OUT_DIR="out_nmapai_$(ts)"; fi
mkdir -p "$OUT_DIR"
LOG_FILE="${OUT_DIR}/nmap_scan.log"

# ---------- Dependencies ----------
require_cmd nmap jq awk sed grep tee xargs
if [[ "$ENABLE_AI" == "true" ]]; then
  require_cmd curl
  [[ -z "${OPENAI_API_KEY:-}" ]] && die "OPENAI_API_KEY is not set but AI analysis is enabled (-a)."
fi
if [[ "$ENABLE_NIKTO" == "true" ]] && ! optional_cmd nikto; then
  warn "Nikto not found; disabling Nikto stage."; ENABLE_NIKTO="false"
fi

# ---------- Sanitize targets ----------
SANITIZED_TARGETS_FILE="${OUT_DIR}/targets_clean.txt"
grep -E -v '^\s*(#|$)' "$IP_LIST_FILE" | sed 's/\r$//' > "$SANITIZED_TARGETS_FILE"
[[ ! -s "$SANITIZED_TARGETS_FILE" ]] && die "No valid targets in $IP_LIST_FILE"
ok "Targets sanitized: $SANITIZED_TARGETS_FILE"

# ---------- DursVuln helpers ----------
check_nmap_version() {
  local vraw vmaj vmin
  vraw="$(nmap --version | head -n1 || true)"
  if [[ "$vraw" =~ version[[:space:]]+([0-9]+)\.([0-9]+) ]]; then
    vmaj="${BASH_REMATCH[1]}"; vmin="${BASH_REMATCH[2]}"
    if (( vmaj < 7 || (vmaj == 7 && vmin < 94) )); then
      warn "Nmap ${vmaj}.${vmin} detected; DursVuln recommends 7.94SVN or newer."
    fi
  fi
}

ensure_dursvuln_ready() {
  [[ "$ENABLE_DURSVULN" != "true" ]] && return 0
  check_nmap_version

  # Ensure we have an NSE script reference
  if [[ "$DURSVULN_USE_GLOBAL" == "true" ]]; then
    : # use --script=dursvuln
  else
    if [[ -z "$DURSVULN_SCRIPT_PATH" ]]; then
      # try common local paths
      for p in "./DursVulnNSE/dursvuln.nse" "./dursvuln.nse"; do
        [[ -f "$p" ]] && { DURSVULN_SCRIPT_PATH="$p"; break; }
      done
    fi
    [[ -z "$DURSVULN_SCRIPT_PATH" || ! -f "$DURSVULN_SCRIPT_PATH" ]] \
      && die "DursVuln enabled but NSE script not found. Use -G (global) or -L /path/to/dursvuln.nse"
  fi

  # DB path: honor -P; else try local; else maybe fetch with -U
  if [[ -z "$DURSVULN_DB_PATH" ]]; then
    for cand in \
      "$(dirname "${DURSVULN_SCRIPT_PATH:-.}")/database/cve-main.json" \
      "./DursVuln-Database/cve-main.json"; do
      [[ -f "$cand" ]] && { DURSVULN_DB_PATH="$cand"; break; }
    done
  fi

  if [[ "$DURSVULN_UPDATE_DB" == "true" ]]; then
    note "Refreshing DursVuln database..."
    # If local repo has updater, prefer it (builds enriched DB)
    if [[ -n "${DURSVULN_SCRIPT_PATH:-}" && -f "$(dirname "$DURSVULN_SCRIPT_PATH")/tools/db_updater.py" ]]; then
      require_cmd python3
      if [[ "$DRY_RUN" != "true" ]]; then
        ( cd "$(dirname "$DURSVULN_SCRIPT_PATH")" && python3 tools/db_updater.py ) \
          || warn "db_updater.py failed; falling back to remote download"
      fi
      DURSVULN_DB_PATH="$(dirname "$DURSVULN_SCRIPT_PATH")/database/cve-main.json"
    fi
    # Fallback: fetch distributable cve-main.json from DB repo
    if [[ "$DRY_RUN" != "true" && ! -f "${DURSVULN_DB_PATH:-/nonexistent}" ]]; then
      require_cmd curl
      mkdir -p "${OUT_DIR}/dursvuln-db"
      DURSVULN_DB_PATH="${OUT_DIR}/dursvuln-db/cve-main.json"
      curl -fsSL "$DURSVULN_DB_RAW_URL" -o "$DURSVULN_DB_PATH" \
        || die "Failed to download cve-main.json from DursVuln-Database repo"
    fi
  fi

  if [[ -z "${DURSVULN_DB_PATH:-}" || ! -f "$DURSVULN_DB_PATH" ]]; then
    warn "cve-main.json not found. Set with -P /path/to/cve-main.json or use -U to download."
  fi

  ok "DursVuln ready (script: ${DURSVULN_USE_GLOBAL:+global}${DURSVULN_SCRIPT_PATH:+$DURSVULN_SCRIPT_PATH}, db: ${DURSVULN_DB_PATH:-<default>})"
}

# ---------- Build Nmap command ----------
NMAP_OUT_NORMAL="${OUT_DIR}/${RESULTS_BASENAME}.nmap"
NMAP_OUT_GREP="${OUT_DIR}/${RESULTS_BASENAME}.gnmap"
NMAP_OUT_XML="${OUT_DIR}/${RESULTS_BASENAME}.xml"

NMAP_CMD=( nmap -iL "$SANITIZED_TARGETS_FILE" )
# shellcheck disable=SC2206
NMAP_CMD+=( ${NMAP_PARAMETERS} )
NMAP_CMD+=( -oN "$NMAP_OUT_NORMAL" -oG "$NMAP_OUT_GREP" -oX "$NMAP_OUT_XML" -v )

if [[ "$ENABLE_DURSVULN" == "true" ]]; then
  ensure_dursvuln_ready
  if [[ "$DURSVULN_USE_GLOBAL" == "true" ]]; then
    NMAP_CMD+=( --script dursvuln )
  else
    NMAP_CMD+=( --script "$DURSVULN_SCRIPT_PATH" )
  fi
  dur_args=()
  [[ -n "$DURSVULN_DB_PATH" ]]      && dur_args+=( "db_path=${DURSVULN_DB_PATH}" )
  [[ -n "$DURSVULN_MIN_SEVERITY" ]] && dur_args+=( "min_severity=${DURSVULN_MIN_SEVERITY}" )
  [[ -n "$DURSVULN_OUTPUT" ]]       && dur_args+=( "dursvuln.output=${DURSVULN_OUTPUT}" )
  (( ${#dur_args[@]} )) && NMAP_CMD+=( --script-args "$(IFS=, ; echo "${dur_args[*]}")" )
fi

note "Nmap command: ${NMAP_CMD[*]}"
log  "Nmap command: ${NMAP_CMD[*]}"

# ---------- Run Nmap ----------
if [[ "$DRY_RUN" == "true" ]]; then
  warn "Dry-run: skipping Nmap execution."
else
  "${NMAP_CMD[@]}" 2>&1 | tee -a "$LOG_FILE" &
  NMAP_PID=$!
  spinner "$NMAP_PID"
  wait "$NMAP_PID" || die "Nmap failed; see $LOG_FILE"
  ok "Nmap completed: $NMAP_OUT_NORMAL | $NMAP_OUT_GREP | $NMAP_OUT_XML"
fi

# ---------- Summaries (CSV/JSON/MD) ----------
CSV_OUT="${OUT_DIR}/nmap_summary.csv"
JSON_OUT="${OUT_DIR}/nmap_summary.json"
MD_OUT="${OUT_DIR}/nmap_summary.md"

if [[ "$DRY_RUN" != "true" ]]; then
  # CSV: host,port,proto,service from .gnmap
  awk '
    /Host: / && /Ports: / {
      host=$2
      ports=$0
      sub(/^.*Ports: /, "", ports)
      n=split(ports, a, ",")
      for (i=1; i<=n; i++) {
        gsub(/^ +| +$/, "", a[i])
        if (a[i] ~ /open/) {
          split(a[i], f, "/")
          port=f[1]; state=f[2]; proto=f[3]; svc=f[5]
          if (state=="open") {
            printf "%s,%s,%s,%s\n", host, port, proto, (svc==""?"-":svc)
          }
        }
      }
    }
  ' "$NMAP_OUT_GREP" | sort -u > "$CSV_OUT" || true

  # JSON
  jq -Rs '
    split("\n") | map(select(length>0)) |
    map(split(",") | {"host": .[0], "port": .[1], "proto": .[2], "service": .[3]})
  ' "$CSV_OUT" > "$JSON_OUT" || echo "[]" > "$JSON_OUT"

  # Markdown per host
  {
    echo "# Nmap Summary"
    echo
    echo "- Generated: $(date -Iseconds)"
    echo "- Sources: \`${RESULTS_BASENAME}.gnmap\`${ENABLE_DURSVULN:+, DursVuln enabled}"
    echo
    jq -r '
      group_by(.host) | .[] |
      ( "## " + .[0].host ),
      "",
      "| Port | Proto | Service |",
      "|------|-------|---------|",
      ( .[] | "| \(.port) | \(.proto) | \(.service) |" ),
      ""
    ' "$JSON_OUT"
  } > "$MD_OUT"

  ok "Summaries: $(basename "$CSV_OUT"), $(basename "$JSON_OUT"), $(basename "$MD_OUT")"
fi

# ---------- Nikto target build & run ----------
NIKTO_OUT_DIR="${OUT_DIR}/nikto"; mkdir -p "$NIKTO_OUT_DIR"
NIKTO_TARGETS_FILE="${OUT_DIR}/nikto_targets.txt"

if [[ "$ENABLE_NIKTO" == "true" && "$DRY_RUN" != "true" ]]; then
  awk -F',' '
    {
      host=$1; port=$2; svc=tolower($4)
      if (svc ~ /http/ || port ~ /^(80|443|8080|8000|8001|8888|8443|5000)$/) {
        print host","port","svc
      }
    }
  ' "$CSV_OUT" | sort -u > "$NIKTO_TARGETS_FILE" || true

  if [[ -s "$NIKTO_TARGETS_FILE" ]]; then
    note "Running Nikto (parallel: ${NIKTO_CONCURRENCY})..."
    < "$NIKTO_TARGETS_FILE" xargs -I{} -P "$NIKTO_CONCURRENCY" bash -c '
      IFS="," read -r host port svc <<< "{}"
      scheme="http"
      if [[ "$port" == "443" || "$port" == "8443" || "$svc" =~ https || "$svc" =~ ssl ]]; then scheme="https"; fi
      out_file="'"$NIKTO_OUT_DIR"'/${host}_${port}.htm"
      echo -e "'"${YELLOW}"'Nikto: ${scheme}://${host}:${port} -> ${out_file}'"'"${NC}"'"
      nikto -h "${scheme}://${host}:${port}" -o "${out_file}" -Format htm >/dev/null 2>&1 || echo "Nikto error for ${host}:${port}" >&2
    '
    ok "Nikto reports: $NIKTO_OUT_DIR"
  else
    warn "No HTTP(S) services detected; skipping Nikto."
  fi
fi

# ---------- DursVuln findings extraction (from .nmap text) ----------
DURSVULN_SUMMARY="${OUT_DIR}/dursvuln_summary.md"
if [[ "$ENABLE_DURSVULN" == "true" && "$DRY_RUN" != "true" ]]; then
  # Extract blocks that start with a line containing "dursvuln" (case-insensitive)
  # and include the subsequent indented lines until a blank line or non-indented line.
  awk '
    BEGIN { IGNORECASE=1; inblock=0 }
    /^Nmap scan report for/ { host=$0; print_host=1; next }
    /dursvuln/ {
      if (print_host==1) {
        print "## " host
        print ""
        print_host=0
      }
      print "```"
      print $0
      inblock=1
      next
    }
    {
      if (inblock==1) {
        if ($0 ~ /^$/) { print "```"; print ""; inblock=0 }
        else if ($0 ~ /^[[:space:]]+\|/ || $0 ~ /^[[:space:]]+|\_/ || $0 ~ /^[[:space:]]+/) { print $0 }
        else { print "```"; print ""; inblock=0 }
      }
    }
    END { if (inblock==1) { print "```"; print "" } }
  ' "$NMAP_OUT_NORMAL" > "$DURSVULN_SUMMARY" || true

  # If empty or trivial, put a note
  if ! grep -q '[^[:space:]]' "$DURSVULN_SUMMARY"; then
    echo "_No DursVuln script output detected in normal report._" > "$DURSVULN_SUMMARY"
  else
    sed -i "1i # DursVuln Findings\n\n_Generated: $(date -Iseconds)_\n" "$DURSVULN_SUMMARY" || true
  fi
  ok "DursVuln findings: $(basename "$DURSVULN_SUMMARY")"
fi

# ---------- Optional AI analysis ----------
AI_OUT_FILE="${OUT_DIR}/ai_analysis.md"
do_ai_chunk() {
  local chunk="$1"
  local payload; payload=$(jq -n --arg c "$chunk" --arg m "$AI_MODEL" --argjson max "$AI_MAX_TOKENS" --argjson temp "$AI_TEMPERATURE" --argjson tp "$AI_TOP_P" '
    {
      "model": $m,
      "messages": [
        {"role": "system", "content": "You are a security analyst. Analyze Nmap and DursVuln findings. Summarize key risks, candidate CVEs, and top 5 prioritized actions. Concise Markdown."},
        {"role": "user", "content": ("Analyze these scan results:\\n\\n" + $c)}
      ],
      "max_tokens": $max, "temperature": $temp, "top_p": $tp
    }')

  local resp http_code body
  resp=$(curl -sS -w "\n%{http_code}" -X POST "$AI_ENDPOINT" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${OPENAI_API_KEY}" \
    -d "$payload") || { echo '{"error":"curl_failed"}'; return 1; }
  http_code=$(echo "$resp" | tail -n1)
  body=$(echo "$resp" | sed '$d')
  [[ "$http_code" == "200" ]] || { echo "{\"error\":\"http_${http_code}\",\"body\":${body}}"; return 1; }
  echo "$body"
}

if [[ "$ENABLE_AI" == "true" && "$DRY_RUN" != "true" ]]; then
  note "Running AI analysis with model: ${AI_MODEL}"
  CORPUS_FILE="${OUT_DIR}/analysis_corpus.txt"
  {
    echo "=== NMAP (.nmap) ==="; cat "$NMAP_OUT_NORMAL" 2>/dev/null || true
    if [[ -f "$DURSVULN_SUMMARY" ]]; then echo; echo "=== DursVuln Summary ==="; cat "$DURSVULN_SUMMARY"; fi
  } > "$CORPUS_FILE"

  CHUNK_SIZE=14000
  tmp_ai="${OUT_DIR}/.ai_chunks"; rm -f "$tmp_ai"; mkdir -p "$tmp_ai"
  split -b "$CHUNK_SIZE" -d -a 3 "$CORPUS_FILE" "${tmp_ai}/part_"

  echo "# AI Analysis" > "$AI_OUT_FILE"
  echo "" >> "$AI_OUT_FILE"
  echo "_Model: ${AI_MODEL}; Generated: $(date -Iseconds)_" >> "$AI_OUT_FILE"
  echo "" >> "$AI_OUT_FILE"

  idx=0
  for part in "${tmp_ai}"/part_*; do
    idx=$((idx+1)); note "Analyzing chunk ${idx}..."
    attempt=0; max_attempts=4; backoff=2
    while : ; do
      attempt=$((attempt+1))
      resp_json="$(do_ai_chunk "$(cat "$part")" || true)"
      if echo "$resp_json" | jq -e '.choices[0].message.content' >/dev/null 2>&1; then
        content=$(echo "$resp_json" | jq -r '.choices[0].message.content')
        { echo "## Chunk ${idx}"; echo; echo "${content}"; echo; } >> "$AI_OUT_FILE"
        ok "AI chunk ${idx} analyzed."; break
      else
        warn "AI request failed (attempt ${attempt}/${max_attempts})."
        if [[ "$attempt" -lt "$max_attempts" ]]; then sleep "$backoff"; backoff=$((backoff*2)); else
          echo "AI failed for chunk ${idx}. Response:" >> "$AI_OUT_FILE"
          echo '```json' >> "$AI_OUT_FILE"; echo "$resp_json" >> "$AI_OUT_FILE"; echo '```' >> "$AI_OUT_FILE"; break
        fi
      fi
    done
  done
  ok "AI analysis: $(basename "$AI_OUT_FILE")"
fi

# ---------- Wrap up ----------
echo
ok "All done."
echo -e "${BLUE}Output folder:${NC} $OUT_DIR"
echo -e "${BLUE}Key files:${NC}
- Nmap: ${RESULTS_BASENAME}.nmap | .gnmap | .xml
- Summaries: $(basename "$CSV_OUT") | $(basename "$JSON_OUT") | $(basename "$MD_OUT")
- DursVuln (if enabled): $(basename "$DURSVULN_SUMMARY")
- Nikto (if enabled): $(basename "$NIKTO_OUT_DIR")/
- Logs: $(basename "$LOG_FILE")
- AI (if enabled): $(basename "$AI_OUT_FILE")
"
