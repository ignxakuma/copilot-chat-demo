from kubernetes.executor import KubectlExecutor
from loguru import logger

class InvestigationService:
    @staticmethod
    def run_full_investigation(namespace: str = "default") -> dict:
        logger.info(f"Starting Kubernetes evidence collection for namespace: {namespace}...")
        
        # We define the flag once, then attach it to every command
        ns_flag = ["-n", namespace]
        
        # 1. Check Pods
        pods_raw = KubectlExecutor.run(["get", "pods"] + ns_flag, as_json=True)
        problematic_pods = []
        if isinstance(pods_raw, dict) and "items" in pods_raw:
            for pod in pods_raw["items"]:
                status = pod.get("status", {}).get("phase", "Unknown")
                container_statuses = pod.get("status", {}).get("containerStatuses", [])
                
                is_healthy = True
                for cs in container_statuses:
                    if not cs.get("ready", False):
                        is_healthy = False
                        state = cs.get("state", {})
                        if "waiting" in state:
                            status = state["waiting"].get("reason", status)
                        elif "terminated" in state:
                            status = state["terminated"].get("reason", status)
                
                if not is_healthy or status not in ["Running", "Succeeded"]:
                    problematic_pods.append({
                        "name": pod["metadata"]["name"],
                        "namespace": pod["metadata"]["namespace"],
                        "status": status
                    })

        # 2. Get Logs for Problematic Pods
        logs_data = {}
        for pod in problematic_pods:
            pod_name = pod["name"]
            log_out = KubectlExecutor.run(["logs", pod_name, "-n", pod["namespace"], "--tail=50"])
            logs_data[pod_name] = log_out if not isinstance(log_out, dict) else log_out.get("error", "Failed to fetch logs")

        # 3. Get Events
        events_raw = KubectlExecutor.run(["get", "events"] + ns_flag, as_json=True)
        events_data = []
        if isinstance(events_raw, dict) and "items" in events_raw:
            sorted_events = sorted(events_raw["items"], key=lambda x: x["metadata"].get("creationTimestamp", ""), reverse=True)
            for event in sorted_events[:20]:
                if event.get("type") == "Warning":
                    events_data.append({
                        "kind": event.get("involvedObject", {}).get("kind"),
                        "name": event.get("involvedObject", {}).get("name"),
                        "reason": event.get("reason"),
                        "message": event.get("message")
                    })

        # 4. Get Deployments
        deps_raw = KubectlExecutor.run(["get", "deployments"] + ns_flag, as_json=True)
        deployments_data = []
        if isinstance(deps_raw, dict) and "items" in deps_raw:
            for dep in deps_raw["items"]:
                ready_replicas = dep.get("status", {}).get("readyReplicas", 0)
                desired_replicas = dep.get("spec", {}).get("replicas", 0)
                if ready_replicas != desired_replicas:
                    deployments_data.append({
                        "name": dep["metadata"]["name"],
                        "ready": ready_replicas,
                        "desired": desired_replicas
                    })

        # 5. Check Networking (Endpoints)
        ep_raw = KubectlExecutor.run(["get", "endpoints"] + ns_flag, as_json=True)
        missing_endpoints = []
        if isinstance(ep_raw, dict) and "items" in ep_raw:
            for ep in ep_raw["items"]:
                if "subsets" not in ep:
                    missing_endpoints.append(ep["metadata"]["name"])

        logger.info("Evidence collection complete.")
        
        return {
            "pods": {
                "healthy": len(problematic_pods) == 0,
                "problematic_pods": problematic_pods
            },
            "logs": logs_data,
            "events": events_data,
            "deployments": deployments_data,
            "network": {
                "missing_endpoints": missing_endpoints
            }
        }