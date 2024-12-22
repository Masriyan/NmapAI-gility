# NmapAIgility

**NmapAIgility** is a powerful and flexible security scanning tool that integrates Nmap and Nikto to analyze web applications for vulnerabilities. Leveraging AI capabilities, it provides insightful analysis of scan results, helping security professionals and enthusiasts identify potential threats effectively.

## Features

- **Nmap Integration:** Perform comprehensive network scans to discover open ports and services.
- **Nikto Scanning:** Analyze web servers for vulnerabilities and misconfigurations.
- **AI-Powered Analysis:** Utilize OpenAI's API to analyze scan results and identify suspicious activities.
- **IPv4 and IPv6 Support:** Scan both IPv4 and IPv6 addresses seamlessly.
- **Customizable Parameters:** Easily customize Nmap scan parameters for tailored results.
- **User-Friendly Output:** Color-coded and formatted output for better readability.

## Prerequisites

Before running **NmapAIgility**, ensure you have the following installed:

- [Nmap](https://nmap.org/download.html)
- [Nikto](https://cirt.net/Nikto2)
- [jq](https://stedolan.github.io/jq/download/)
- [curl](https://curl.se/download.html)

## Installation

1. Clone the repository:
bash git clone https://github.com/yourusername/NmapAIgility.git cd NmapAIgility

2. Make the script executable:
bash chmod +x scripts/nmapai_gility.sh

3. Install the required tools (if not already installed):
   - For Debian/Ubuntu:
bash sudo apt-get install nmap nikto jq curl


## Usage
Run the script with the following command:

bash ./scripts/nmapai_gility.sh <ip_list_file> <nmap_parameters>

### Example

bash ./scripts/nmapai_gility.sh ip_list.txt -sS -p 80,443

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please fork the repository and submit a pull request.

1. Fork the repository.
2. Create your feature branch:
bash git checkout -b feature/YourFeature

3. Commit your changes:
bash git commit -m "Add some feature"

4. Push to the branch:
bash git push origin feature/YourFeature

5. Open a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Nmap](https://nmap.org/) for network scanning capabilities.
- [Nikto](https://cirt.net/Nikto2) for web server vulnerability scanning.
- [OpenAI](https://openai.com/) for providing AI analysis capabilities.
