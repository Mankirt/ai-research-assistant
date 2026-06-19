def get_fact_checker_prompt(research_output: dict) -> str:
    facts_list = "\n".join(
        f"- {fact}" for fact in research_output.get("key_facts", [])
    )
    sources_list = "\n".join(
        f"- {source}" for source in research_output.get("credible_sources", [])
    )

    return f"""You are a fact-checking analyst. Your job is to evaluate claims
        for credibility based on the sources provided.

        TOPIC: {research_output.get('topic', '')}

        CLAIMED FACTS:
        {facts_list}

        SOURCES:
        {sources_list}

        CONFLICTING INFO ALREADY NOTED:
        {research_output.get('conflicting_info', [])}

        Your task:
        1. Rate each fact's credibility as "high", "medium", or "low" based on source quality
        2. Flag any facts that seem unverifiable or overly broad
        3. Note if multiple independent sources support a fact (higher confidence) vs single source

        Respond in this exact JSON format:
        {{
            "topic": "{research_output.get('topic', '')}",
            "verified_facts": [
                {{"fact": "fact text", "confidence": "high", "reasoning": "brief reason"}}
            ],
            "flagged_facts": ["fact that seems unreliable or unverifiable"],
            "overall_credibility_score": "high",
            "notes": "1-2 sentence summary of fact-checking findings"
        }}

        Respond with JSON only. No preamble, no explanation, no markdown code fences.
        """