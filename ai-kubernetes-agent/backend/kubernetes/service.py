from kubernetes.inspectors import ClusterInspectors
from loguru import logger

class InvestigationService:
    @staticmethod
    def run_full_investigation() -> dict:
        logger.info("Starting Kubernetes evidence collection...")
        
        pods = ClusterInspectors.check_pods()
        
        # Only pull logs if there are broken pods
        logs = {}
        if not pods.get("healthy", True) and "problematic_pods" in pods:
            logs = ClusterInspectors.collect_logs(pods["problematic_pods"])
            
        events = ClusterInspectors.analyze_events()
        deployments = ClusterInspectors.inspect_deployments()
        network = ClusterInspectors.check_networking()
        
        logger.info("Evidence collection complete.")
        
        return {
            "pods": pods,
            "logs": logs,
            "events": events,
            "deployments": deployments,
            "network": network
        }