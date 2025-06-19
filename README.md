> A chatbot-style web app for querying Kubernetes pod logs using natural language. Built with Flask, Bootstrap, and the Kubernetes Python client.

---

### 📘 **README.md Template**

````markdown
# 🤖 LogBot - Kubernetes Log Chatbot

LogBot is a chatbot-style web application that helps you query and view logs from Kubernetes pods using natural language. It's built with Flask (Python) on the backend and a sleek Bootstrap frontend. Ideal for DevOps teams, SREs, and developers who want a quicker way to inspect logs without `kubectl`.

---

## 🔧 Features

- 🔍 Ask questions like “show me error logs” or “debug logs from job dev/webapp”
- 📂 Filter logs by namespace, pod, and number of lines
- 💬 Chat-style log viewing interface
- 📊 Log summarization with error/warning/info/debug count
- 💡 Keyword detection (error, warn, info, debug, or custom phrase)
- 🌐 REST API endpoints for integration
- 🛡️ Graceful error handling

---

## 📸 Screenshots
![image](https://github.com/user-attachments/assets/fda38c70-7ef5-4935-8f8f-17b97d842aab)

![image](https://github.com/user-attachments/assets/619fa2a1-c888-4288-9382-7d0cea466cc5)

![image](https://github.com/user-attachments/assets/151d2e22-17bf-4c10-9326-feb80bf5e297)

---

## 🏗️ Tech Stack

- **Backend**: Flask, Kubernetes Python Client
- **Frontend**: HTML, Bootstrap 5, JavaScript
- **Deployment**: Kubernetes-ready, or run locally

---

## 🚀 Getting Started

### 📦 Prerequisites

- Python 3.8+
- `kubectl` configured with access to your cluster
- Access to Kubernetes logs

### 🛠️ Installation

```bash
git clone https://github.com/your-username/logbot-k8s.git
cd logbot-k8s
pip install -r requirements.txt
python chat_bot.py
````

Visit [http://localhost:8099](http://localhost:8099)

---

## 📂 Project Structure

```
logbot-k8s/
├── chat_bot.py        # Flask app with Kubernetes log API
├── templates/
│   └── chat.html      # Frontend chat UI
├── static/            # Optional: for CSS/JS if separated
├── screenshots/       # Project screenshots
└── README.md
```

---

## 🔗 API Endpoints

| Method | Endpoint      | Description                    |
| ------ | ------------- | ------------------------------ |
| GET    | `/`           | Loads the chat UI              |
| GET    | `/namespaces` | Fetches available namespaces   |
| GET    | `/pods/<ns>`  | Lists pods in a namespace      |
| POST   | `/chat`       | Sends user query, returns logs |

---

## 🧠 Example Queries

* `show me error logs`
* `debug logs from job myns/backend`
* `"connection refused"`
* `job prod/api show all logs`

---

## 📊 Sample Summary Output

```
🔢 Total Log Lines: 132
❌ Errors: 12
⚠️ Warnings: 15
ℹ️ Info: 77
🐞 Debug: 28
```

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Riyaz** – https://github.com/Riyazkokkada/logbot-k8s

---

## ⭐️ Show Your Support

If you like this project, please ⭐ the repo and share it!

```
