from providers.openai_provider import OpenAIProvider

provider = OpenAIProvider()

print(provider.generate_response("Hello AOIP"))