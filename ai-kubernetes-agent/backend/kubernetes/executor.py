import subprocess
import json
import os
from loguru import logger

class KubectlExecutor:
    @staticmethod
    def run(args: list[str], as_json: bool = False) -> any:
        # Point directly to the newly mounted internal config
        env = os.environ.copy()
        env["KUBECONFIG"] = "/root/.kube/config"

        cmd = ["kubectl"] + args
        if as_json and "-o" not in args:
            cmd.extend(["-o", "json"])
            
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, env=env, check=True
            )
            if as_json:
                return json.loads(result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Kubectl Command Failed: {' '.join(cmd)}")
            logger.error(f"Error: {e.stderr}")
            return {"error": e.stderr.strip()} if as_json else f"Error: {e.stderr.strip()}"