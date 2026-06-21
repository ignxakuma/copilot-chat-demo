from ai.prompt_builder import PromptBuilder
from ai.llm_client import CopilotLLMClient
from loguru import logger

class RootCauseAnalyzer:
    @staticmethod
    async def analyze(evidence: dict) -> dict:
        logger.info("Building structured AI reasoning prompt...")
        prompt = PromptBuilder.build(evidence)
        
        logger.info("Executing Senior SRE Analysis...")
        diagnosis = await CopilotLLMClient.analyze_evidence(prompt)
        
        return diagnosis