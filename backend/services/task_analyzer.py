class TaskAnalyzer:

    def analyze(self, messages):
        text = messages[-1].content.lower()

        if any(word in text for word in [
            "python", "java", "code", "bug", "api",
            "function", "class", "program"
        ]):
            return "coding"

        elif any(word in text for word in [
            "write", "essay", "email", "article", "blog"
        ]):
            return "writing"

        elif any(word in text for word in [
            "summarize", "summary", "shorten"
        ]):
            return "summarization"

        elif any(word in text for word in [
            "translate", "translation", "hindi",
            "kannada", "tamil", "french"
        ]):
            return "translation"

        elif any(word in text for word in [
            "why", "compare", "difference", "explain"
        ]):
            return "reasoning"

        return "general"