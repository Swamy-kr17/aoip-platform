from google import genai

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Say hello."
)

print(response.text)