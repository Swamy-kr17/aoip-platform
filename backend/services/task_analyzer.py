import re


class TaskAnalyzer:
    def analyze(self, messages):
        text = messages[-1].content.lower()

        if any(re.search(rf"\b{re.escape(word)}\b", text) for word in [
            "python", "java", "code", "bug", "api",
            "function", "class", "program"
        ]):
            return "coding"

        elif any(re.search(rf"\b{re.escape(word)}\b", text) for word in [
            "write", "essay", "email", "article", "blog"
        ]):
            return "writing"

        elif any(re.search(rf"\b{re.escape(word)}\b", text) for word in [
            "summarize", "summary", "shorten"
        ]):
            return "summarization"

        elif any(re.search(rf"\b{re.escape(word)}\b", text) for word in [
            "translate", "translation", "hindi",
            "kannada", "tamil", "french"
        ]):
            return "translation"

        elif any(re.search(rf"\b{re.escape(word)}\b", text) for word in [
            "why", "compare", "difference", "explain"
        ]):
            return "reasoning"

        return "general"
