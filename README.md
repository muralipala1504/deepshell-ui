

# 💻 Deepshell UI

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)  
_A lightweight web UI for the **Deepshell** AI Shell Assistant._

---

## 🚀 What is Deepshell UI?

Deepshell UI provides a **clean and interactive web interface** for working with the **Deepshell backend** AI-powered shell assistant.  
It is designed for **Linux Sysadmins, DevOps Engineers, Cloud Engineers, and IaC Specialists** who need a fast, lightweight way to generate and test commands using LLMs.

---

## ✨ Features

- Intuitive **chat-style interface**
- Syntax-highlighted shell script output with **Copy-to-Clipboard**
- Compact & responsive layout with scrollable responses
- Seamless connection to the **Deepshell backend API**

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, Vanilla JS, Prism.js (syntax highlighting & copy-to-clipboard)  
- **Backend**: FastAPI, Uvicorn, Typer, OpenAI (via LiteLLM), psutil, Rich  
- **Other**: YAML for config, Python 3.9+

---

## 🖼️ Preview

![Deepshell UI Screenshot](docs/screenshot.png)  
*Example: AI‑generated LVM shell script created instantly via Deepshell Chat UI*

---

## ⚡ Getting Started

### Prerequisites
- Python **3.9+**
- Git  
- OpenAI API Key (required for backend AI calls)

### Installation

```bash
git clone https://github.com/muralipala1504/deepshell-ui.git
cd deepshell-ui

```

Install dependencies:

```bash

pip install -r deepshell-backend/requirements.txt
pip install -e deepshell-backend/

```

Set your OpenAI API key:

Linux/macOS

```bash

export OPENAI_API_KEY="your_openai_api_key_here"

```

Windows PowerShell

```pshell

$env:OPENAI_API_KEY="your_openai_api_key_here"

```

Run the backend

```bash

python run_deepshell.py > deepshell.log 2>&1 &

```

Now open in browser:

```bash

http://localhost:8001

```

👉 If remote, replace localhost with your server IP


⚡ Firewall Config (Linux Only)


```bash

sudo firewall-cmd --add-port=8001/tcp --permanent
sudo firewall-cmd --reload

```

🛑 Stopping the Server

In the terminal where run_deepshell.py is running, press:

Ctrl + C

🤝 Contributing

Contributions are always welcome!

    Open issues
    Submit PRs

Help shape the future of Deepshell 🚀


📜 License

This project is licensed under the MIT License.
See the LICENSE file for details.


---

## 🛣️ Roadmap

Here are some planned improvements to **Deepshell UI**:

- [ ] 🌙 Dark mode theme for the UI  
- [ ] 💾 Persistent chat history (store + reload previous conversations)  
- [ ] 📂 Export responses to file (save scripts directly)  
- [ ] ⚡ Support for multiple LLM providers (OpenAI, Anthropic, Local LLMs)  
- [ ] 🔄 Clear/Reset chat session button  
- [ ] 🛠️ More sysadmin/devops‑friendly features (cloud CLI, ansible, terraform hints)  

---

✅ Contributions are welcome! Feel free to open PRs/issues for features, fixes, and ideas.
____________________________________________________________________

---

