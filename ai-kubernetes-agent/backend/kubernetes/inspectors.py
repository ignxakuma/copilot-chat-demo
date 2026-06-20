from kubernetes.executor import KubectlExecutor

class ClusterInspectors:
    
    @staticmethod
    def check_pods() -> dict:
        data = KubectlExecutor.run(["get", "pods", "-A"], as_json=True)
        if "error" in data: return data
        
        problematic_pods = []
        for item in data.get("items", []):
            status = item.get("status", {}).get("phase")
            container_statuses = item.get("status", {}).get("containerStatuses", [])
            
            # Surface deeper errors like CrashLoopBackOff or ImagePullBackOff
            for cs in container_statuses:
                state = cs.get("state", {})
                if "waiting" in state and state["waiting"].get("reason"):
                    status = state["waiting"]["reason"]
            
            if status not in ["Running", "Succeeded"]:
                problematic_pods.append({
                    "name": item["metadata"]["name"],
                    "namespace": item["metadata"]["namespace"],
                    "status": status
                })
                
        return {
            "healthy": len(problematic_pods) == 0,
            "problematic_pods": problematic_pods
        }

    @staticmethod
    def collect_logs(problematic_pods: list) -> dict:
        logs = {}
        for pod in problematic_pods:
            # Grab only the last 50 lines to avoid overwhelming the future LLM
            output = KubectlExecutor.run(["logs", pod["name"], "-n", pod["namespace"], "--tail=50"])
            logs[pod["name"]] = output
        return logs

    @staticmethod
    def analyze_events() -> list:
        data = KubectlExecutor.run(["get", "events", "-A"], as_json=True)
        if "error" in data: return data
        
        warnings = []
        for item in data.get("items", []):
            if item.get("type") == "Warning":
                warnings.append({
                    "kind": item.get("involvedObject", {}).get("kind"),
                    "name": item.get("involvedObject", {}).get("name"),
                    "reason": item.get("reason"),
                    "message": item.get("message")
                })
        return warnings

    @staticmethod
    def inspect_deployments() -> list:
        data = KubectlExecutor.run(["get", "deployments", "-A"], as_json=True)
        if "error" in data: return data
        
        unhealthy = []
        for item in data.get("items", []):
            spec_replicas = item.get("spec", {}).get("replicas", 1)
            ready_replicas = item.get("status", {}).get("readyReplicas", 0)
            
            if spec_replicas != ready_replicas:
                unhealthy.append({
                    "name": item["metadata"]["name"],
                    "namespace": item["metadata"]["namespace"],
                    "desired": spec_replicas,
                    "ready": ready_replicas
                })
        return unhealthy

    @staticmethod
    def check_networking() -> dict:
        services = KubectlExecutor.run(["get", "svc", "-A"], as_json=True)
        endpoints = KubectlExecutor.run(["get", "endpoints", "-A"], as_json=True)
        
        if "error" in services: return services
        
        missing_endpoints = []
        for ep in endpoints.get("items", []):
            # If an endpoint has no subsets, the Service is routing to nowhere
            if not ep.get("subsets"):
                missing_endpoints.append({
                    "service": ep["metadata"]["name"],
                    "namespace": ep["metadata"]["namespace"],
                    "issue": "No backing pods found (empty endpoints)"
                })
        return {"missing_endpoints": missing_endpoints}