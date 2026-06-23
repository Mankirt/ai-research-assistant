def get_writer_prompt(fact_check_output: dict) -> str:
    verified_facts_list = "\n".join(
        f"- {vf['fact']} (confidence: {vf['confidence']}) — {vf['reasoning']}"
        for vf in fact_check_output.get("verified_facts", [])
    )
    flagged_list = "\n".join(
        f"- {fact}" for fact in fact_check_output.get("flagged_facts", [])
    )

    return f"""You are a research writer. Your job is to turn verified facts
        into a clear, well-organized report.

        TOPIC: {fact_check_output.get('topic', '')}

        VERIFIED FACTS:
        {verified_facts_list}

        FLAGGED / UNVERIFIED CLAIMS (mention with caution, do not present as certain):
        {flagged_list}

        OVERALL CREDIBILITY: {fact_check_output.get('overall_credibility_score', '')}
        NOTES FROM FACT CHECKER: {fact_check_output.get('notes', '')}

        Your task:
        Write a clear, well-structured markdown report covering this topic. Use the
        verified facts as your primary content. If you mention flagged claims, note
        they are unverified. Keep it factual and well-organized with headers.

        Respond in this exact JSON format:
        {{
            "topic": "{fact_check_output.get('topic', '')}",
            "title": "A clear, engaging title for the report",
            "report_markdown": "The full markdown report as a single string, using \\n for line breaks",
            "word_count": 0
        }}

        Respond with JSON only. No preamble, no explanation, no markdown code fences
        around the JSON itself (the report_markdown field should contain markdown,
        but the outer response must be raw JSON).
        """