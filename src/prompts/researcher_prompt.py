def get_researcher_prompt(topic: str, search_results: list[dict]) -> str:
    formatted_sources = ""
    for i, result in enumerate(search_results, 1):
        formatted_sources += f"""
                Source {i}:
                Title: {result['title']}
                URL: {result['url']}
                Content: {result['content']}
                ---
            """

    return f"""You are a research analyst. Your job is to analyze search results
                and extract the most relevant, accurate information about a given topic.

                TOPIC: {topic}

                SEARCH RESULTS:
                {formatted_sources}

                Your task:
                1. Identify the most important facts about this topic from the sources
                2. Note any conflicting information across sources
                3. List the most credible sources

                Respond in this exact JSON format:
                {{
                    "topic": "{topic}",
                    "key_facts": ["fact 1", "fact 2", "fact 3"],
                    "conflicting_info": ["conflict 1 if any"],
                    "credible_sources": ["url1", "url2"],
                    "summary": "2-3 sentence summary of findings"
                }}

                Respond with JSON only. No preamble, no explanation.
            """