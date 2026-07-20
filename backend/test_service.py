from services.ai_service import AIService

ai = AIService()

prompt = input("Enter your prompt: ")

response = ai.ask_ai(prompt)

print("\nAI Response:\n")
print(response)