#!/bin/bash

# Hardcoded OpenAI API key
OPENAI_API_KEY="PUT YOUR OpenAI key Here / Masukan Open Ai Key disini"

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if the input file is provided
if [ "$#" -lt 2 ]; then
    echo -e "${RED}Usage: $0 <ip_list_file> <nmap_parameters>${NC}"
    exit 1
fi

IP_LIST_FILE=$1
shift  # Shift the parameters to get the rest as Nmap parameters
NMAP_PARAMETERS="$@"
RESULTS_FILE="nmap_results.txt"
LOG_FILE="nmap_scan.log"
NIKTO_RESULTS_FILE="nikto_results.txt"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}jq is not installed. Please install jq to parse JSON responses.${NC}"
    exit 1
fi

# Function to show a loading animation
loading() {
    local pid=$1
    local delay=0.5
    local spin='/-\|'
    local i=0
    while ps -p $pid > /dev/null; do
        local temp=${spin:i++%${#spin}:1}
        printf "\r${CYAN}Loading... ${temp}${NC}"
        sleep $delay
    done
    printf "\r${GREEN}Done!${NC}\n"
}

# Perform nmap scan and save results with verbose output
echo -e "${BLUE}Scanning IP addresses from $IP_LIST_FILE with parameters: $NMAP_PARAMETERS...${NC}"
nmap -iL "$IP_LIST_FILE" $NMAP_PARAMETERS -oN "$RESULTS_FILE" -v | tee "$LOG_FILE" &

# Show loading animation while nmap is running
loading $!

# Check if nmap was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Nmap scan failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Nmap scan completed. Results saved to $RESULTS_FILE.${NC}"

# Run Nikto against the discovered hosts
echo -e "${BLUE}Running Nikto scan on discovered hosts...${NC}"
while read -r ip; do
    if [[ $ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ || $ip =~ ^[0-9a-fA-F:]+$ ]]; then
        echo -e "${YELLOW}Scanning $ip with Nikto...${NC}"
        nikto -h "$ip" -o "$NIKTO_RESULTS_FILE" -F htm >> "$NIKTO_RESULTS_FILE"
    fi
done < <(grep "Nmap scan report for" "$RESULTS_FILE" | awk '{print $5}')

# Check if Nikto was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Nikto scan failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Nikto scan completed. Results saved to $NIKTO_RESULTS_FILE.${NC}"

# Send results to ChatGPT for analysis
echo -e "${BLUE}Sending results to ChatGPT for analysis...${NC}"

ANALYSIS=$(curl -s -X POST https://api.openai.com/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-d '{
  "model": "gpt-3.5-turbo",
  "messages": [{"role": "user", "content": "Analyze the following nmap scan results and identify any suspicious activities: '"$(cat $RESULTS_FILE | tr '\n' ' ')"'"}],
  "max_tokens": 300
}')

# Check if curl was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to send request to OpenAI API.${NC}"
    exit 1
fi

# Extract and display the analysis
echo -e "${GREEN}Analysis Result:${NC}"
echo "$ANALYSIS" | jq -r '.choices[0].message.content'
