def get_critic_prompt(writer_output: dict) -> str:
            return f"""You are a senior editor reviewing a web-researched report.
        This report was produced by an AI research pipeline using live web sources.
        Evaluate it fairly against the standard of a well-written web research summary,
        NOT an academic paper or peer-reviewed article.

        TOPIC: {writer_output.get('topic', '')}

        REPORT TITLE: {writer_output.get('title', '')}

        REPORT CONTENT:
        {writer_output.get('report_markdown', '')}

        Your task:
        1. Score the report from 1-10 based on clarity, structure, and usefulness
        for someone wanting a well-rounded overview of the topic
        2. Identify 2-3 specific weaknesses relative to a web research summary standard
        3. Suggest 2-3 concrete improvements
        4. Give a final verdict:
        - "approved" if score >= 6 (meets standard for a web research summary)
        - "needs_revision" if score < 6 (significant issues with clarity or structure)

        Be fair and constructive. A report that clearly explains the topic with good
        structure and covers key aspects deserves a score of 7 or higher, even without
        academic citations.

        Respond in this exact JSON format:
        {{
            "topic": "{writer_output.get('topic', '')}",
            "score": 0,
            "weaknesses": ["weakness 1", "weakness 2"],
            "suggested_improvements": ["improvement 1", "improvement 2"],
            "verdict": "approved",
            "critique_summary": "2-3 sentence overall critique"
        }}

        Respond with JSON only. No preamble, no explanation, no markdown code fences.
        """