
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
- Easy to run locally using Docker

---

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine
- OpenAI API key (required for backend AI calls)

### Running DeepShell UI with Docker Compose

1. Clone this repository:

```bash
git clone https://github.com/muralipala1504/deepshell-ui.git
cd deepshell-ui

```
Set your OpenAI API key as an environment variable:

```
export OPENAI_API_KEY="your_openai_api_key_here"

```

Build and start the containers:

```

docker compose build
docker compose up -d

```

Open your browser and navigate to:

http://localhost:8001

```

Start interacting with DeepShell via the UI!


	About the Backend

	The DeepShell backend powers the AI shell assistant. It is included as a 	subfolder in this repo.

	For detailed backend documentation, please see the archive/backend-docs/ 	folder or visit the DeepShell backend repository.


Contributing

Contributions are welcome! Please open issues or pull requests for improvements.


License

This project is licensed under the MIT License. See the LICENSE file for details.


```
