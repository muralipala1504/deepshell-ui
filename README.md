
```
# DeepShell UI

Welcome to the DeepShell UI project — a user-friendly web interface for interacting with the DeepShell backend AI shell assistant.

---

## What is DeepShell UI?

DeepShell UI provides a clean, interactive web interface to send commands and receive AI-generated shell scripts and responses powered by the DeepShell backend.

---

## Features

- Intuitive web interface with prompt input and response display
- Syntax-highlighted shell script output with copy-to-clipboard
- Connects seamlessly to the DeepShell backend API
- Easy to run locally with minimal setup

---

## Getting Started

### Prerequisites

- Python 3.9 or higher installed
- Git installed
- OpenAI API key (required for backend AI calls)

---

### Installation Steps

1. **Clone this repository:**

```bash
git clone https://github.com/muralipala1504/deepshell-ui.git
cd deepshell-ui

```

Install Python dependencies:

```bash

pip install -r deepshell-backend/requirements.txt

```

Install the local DeepShell package:

```bash

pip install -e deepshell-backend/

```

Set your OpenAI API key as an environment variable:

	On Linux/macOS:

```bash

export OPENAI_API_KEY="your_openai_api_key_here"

```

	On Windows PowerShell:

```pshell

$env:OPENAI_API_KEY="your_openai_api_key_here"

```

Running DeepShell UI

Start the backend and UI server with the launcher script:

```bash

python run_deepshell.py

```

You should see a message indicating the backend has started.


Accessing the UI

Open your web browser and navigate to:

http://localhost:8001  

You can now interact with DeepShell UI.

Stopping the Server

To stop the backend server, go to the terminal where run_deepshell.py is running and press:

Ctrl + C


About the Backend

The DeepShell backend powers the AI shell assistant. It is included as a subfolder in this repo.

For detailed backend documentation, please see the archive/backend-docs/ folder or visit the DeepShell backend repository.

Contributing

Contributions are welcome! Please open issues or pull requests for improvements.

License

This project is licensed under the MIT License. See the LICENSE file for details.

---

```
