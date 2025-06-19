from flask import Flask, render_template, request, jsonify
from kubernetes import client, config
from flask_cors import CORS
import re
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
except Exception as e:
    logging.error(f"❌ Failed to load kube config: {e}")
    v1 = None


def parse_query(user_input, default_namespace=None):
    namespace, container, keyword = default_namespace, None, None

    # Match job style "job namespace/container"
    job_match = re.search(r'job\s+([\w-]+)/([\w-]+)', user_input, re.IGNORECASE)
    if job_match:
        namespace = job_match.group(1)
        container = job_match.group(2)

    lowered = user_input.lower()

    if re.search(r'\b(show (me )?all logs|all logs)\b', lowered):
        keyword = None  # No filtering — fetch all logs
    else:
        if "error" in lowered:
            keyword = "error"
        elif "warn" in lowered:
            keyword = "warn"
        elif "info" in lowered:
            keyword = "INFO"
        elif "debug" in lowered:
            keyword = "DEBUG"
        else:
            quoted = re.findall(r'"([^"]+)"', user_input)
            keyword = quoted[0] if quoted else user_input.strip()

    return namespace, container, keyword


def get_pods(namespace):
    if not v1:
        return []
    try:
        pods = v1.list_namespaced_pod(namespace=namespace)
        return sorted([pod.metadata.name for pod in pods.items])
    except Exception as e:
        logging.error(f"❌ Error fetching pods for namespace '{namespace}': {e}")
        return []


def get_logs_from_k8s(namespace, keyword, pod_name=None, container=None, limit=50):
    MAX_LIMIT = 1000
    limit = min(limit, MAX_LIMIT)

    if not v1:
        return ["⚠️ Kubernetes client is not initialized."]

    pods_to_check = []

    if pod_name:
        # Validate pod existence in namespace
        pods = get_pods(namespace)
        if pod_name not in pods:
            return [f"⚠️ Pod '{pod_name}' not found in namespace '{namespace}'."]
        pods_to_check = [pod_name]
    else:
        try:
            pods = v1.list_namespaced_pod(namespace=namespace)
            pods_to_check = [pod.metadata.name for pod in pods.items]
        except Exception as e:
            return [f"⚠️ Error fetching pods in namespace '{namespace}': {str(e)}"]

    logs = []
    for pod in pods_to_check:
        try:
            pod_obj = v1.read_namespaced_pod(name=pod, namespace=namespace)
            containers = [c.name for c in pod_obj.spec.containers]
            target_containers = [container] if container and container in containers else containers

            for c in target_containers:
                try:
                    log_output = v1.read_namespaced_pod_log(
                        name=pod,
                        namespace=namespace,
                        container=c,
                        tail_lines=limit,
                        timestamps=True
                    )

                    if keyword:
                        filtered_lines = [
                            line for line in log_output.splitlines()
                            if keyword.lower() in line.lower()
                        ]
                    else:
                        filtered_lines = log_output.splitlines()

                    for idx, line in enumerate(filtered_lines, 1):
                        parts = line.split(" ", 1)
                        if len(parts) == 2:
                            timestamp, msg = parts
                            formatted_line = f"{idx:4d}. [{pod}/{c}] {timestamp} {msg}"
                        else:
                            formatted_line = f"{idx:4d}. [{pod}/{c}] {line}"
                        logs.append(formatted_line)

                except Exception as e:
                    logs.append(f"[{pod}/{c}] ⚠️ Failed to fetch logs: {str(e)}")

        except Exception as e:
            logs.append(f"[{pod}] ⚠️ Failed to read pod info: {str(e)}")

    return logs if logs else ["⚠️ No logs found."]


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/namespaces")
def namespaces():
    if not v1:
        return jsonify({"namespaces": [], "error": "Kubernetes client not initialized."})
    try:
        ns_list = v1.list_namespace()
        namespaces = sorted([ns.metadata.name for ns in ns_list.items])
        return jsonify({"namespaces": namespaces})
    except Exception as e:
        logging.error(f"❌ Error listing namespaces: {e}")
        return jsonify({"namespaces": [], "error": str(e)})


@app.route("/pods/<namespace>")
def pods(namespace):
    pods_list = get_pods(namespace)
    return jsonify({"pods": pods_list})


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        namespace = data.get("namespace", "").strip() or None
        pod = data.get("pod", "").strip() or None
        limit = int(data.get("limit", 50))

        if not user_message:
            return jsonify({"reply": ["Please enter a search keyword."]})

        ns, container, keyword = parse_query(user_message, namespace)
        if not ns:
            return jsonify({"reply": ["Please select or specify a namespace."]})

        logs = get_logs_from_k8s(ns, keyword, pod_name=pod, container=container, limit=limit)
        return jsonify({"reply": logs})

    except Exception as e:
        logging.exception("🔥 Exception during /chat request:")
        return jsonify({"reply": [f"⚠️ Internal server error: {str(e)}"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090, debug=True)
