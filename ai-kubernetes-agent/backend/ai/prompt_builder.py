import json

class PromptBuilder:
    @staticmethod
    def build(evidence: dict) -> str:
        return f"""You are a Senior Kubernetes SRE diagnosing a cluster incident.
Analyze the following cluster evidence and determine the root cause. 
Correlate pod statuses, logs, and events to provide an accurate diagnosis.

EVIDENCE:
{json.dumps(evidence, indent=2)}

OUTPUT FORMAT:
You must respond with ONLY a raw JSON object. Do not include markdown formatting, backticks, or conversational text. Use the exact keys below:
{{
  "root_cause": "Brief summary of the exact failure.",
  "explanation": "Detailed correlation of why it failed based on logs and events.",
  "fix": "Actionable, beginner-friendly steps to resolve the issue.",
  "kubectl_command": "The exact kubectl command(s) needed to apply the fix.",
  "prevention": "How to prevent this in the future.",
  "confidence": 95
}}
"""