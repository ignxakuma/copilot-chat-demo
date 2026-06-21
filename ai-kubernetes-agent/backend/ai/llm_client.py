import os
import json
from loguru import logger
from copilot import CopilotClient

class CopilotLLMClient:
    @staticmethod
    async def analyze_evidence(prompt_text: str) -> dict:
        if not os.getenv("COPILOT_GITHUB_TOKEN"):
            logger.error("COPILOT_GITHUB_TOKEN is missing!")
            return CopilotLLMClient._fallback_error("Missing Copilot Token in .env")

        try:
            logger.info("Initializing GitHub Copilot SDK...")
            # The SDK automatically authenticates using the COPILOT_GITHUB_TOKEN env variable
            client = CopilotClient()
            await client.start()
            
            # Establish an agentic session requesting Claude (Pass as keyword argument)
            session = await client.create_session(model="auto")
            
            logger.info("Sending Kubernetes evidence to AI for reasoning...")
            # Send the prompt as a keyword argument
            response = await session.send_and_wait(prompt=prompt_text)
            
            raw_content = response.data.content
            await client.stop()
            
            # Clean potential markdown formatting (```json) returned by the LLM
            cleaned_content = raw_content.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_content)

        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response into JSON. Raw: {raw_content}")
            return CopilotLLMClient._fallback_error("LLM returned malformed data instead of JSON.")
        except Exception as e:
            logger.error(f"Copilot SDK Execution Error: {str(e)}")
            return CopilotLLMClient._fallback_error(str(e))

    @staticmethod
    def _fallback_error(reason: str) -> dict:
        return {
            "root_cause": "AI Analysis Failed",
            "explanation": f"The LLM client encountered an error: {reason}",
            "fix": "Check backend container logs for SDK or network issues.",
            "kubectl_command": "docker compose logs backend",
            "prevention": "Ensure valid token and Copilot API availability.",
            "confidence": 0
        }