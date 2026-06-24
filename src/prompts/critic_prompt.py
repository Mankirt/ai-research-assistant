def get_critic_prompt(writer_output: dict) -> str:
    return f"""You are a critical reviewer evaluating a research report for quality.

            TOPIC: {writer_output.get('topic', '')}

            REPORT TITLE: {writer_output.get('title', '')}

            REPORT CONTENT:
            {writer_output.get('report_markdown', '')}

            Your task:
            1. Score the report from 1-10 on clarity, structure, and usefulness
            2. Identify specific weaknesses (e.g. missing context, weak sourcing, bias, vague claims)
            3. Suggest 2-3 concrete improvements
            4. Give a final verdict: "approved" if score >= 7, "needs_revision" if below 7

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