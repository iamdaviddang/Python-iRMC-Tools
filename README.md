
# Python iRMC Tools

This project is a Python-based toolkit for interacting with iRMC (integrated Remote Management Controller) systems. It allows system administrators to manage and monitor remote systems using command-line tools.

## Features

- Command-line interface (CLI) to control and monitor systems via iRMC.
- Python-based solution for automating system management tasks.
- Supports basic functionalities like rebooting systems, checking status, and more.
- Easily extendable to add more iRMC functionalities.

## Prerequisites

To run this project, you will need:

- Python 3.6 or higher
- A working iRMC setup

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/iamdaviddang/Python-iRMC-Tools.git
   cd Python-iRMC-Tools
   ```

2. **Set up a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

After setting up the environment and installing dependencies, you can use the CLI to interact with iRMC systems.

1. **Running the tool**:

   To run the tool, use the following command:

   ```bash
   python irmc_tool.py [COMMAND] [OPTIONS]
   ```

   Replace `[COMMAND]` with the action you want to perform (e.g., reboot, status) and `[OPTIONS]` with any additional parameters.

2. **Example**:

   ```bash
   python irmc_tool.py reboot --host 192.168.1.100
   ```

   This command will reboot the system with the IP address `192.168.1.100`.

## Future Enhancements

- Add support for more iRMC features (e.g., power management, detailed system diagnostics).
- Improve error handling and logging.
- Add unit tests to ensure reliability and stability.

## Contributing

If you'd like to contribute, feel free to submit pull requests or open issues for discussions on features and improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for more details.

