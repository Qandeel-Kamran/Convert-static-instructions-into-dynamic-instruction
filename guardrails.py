from decouple import config
import openai
import asyncio
import re

openai.api_key = config("OPENAI_API_KEY")

print("API Key loaded:", bool(openai.api_key))  # Check if key loads

MAX_API_CALLS = 3  # Max allowed API calls for testing
api_call_count = 0  # Counter for API calls made

def is_math_query(prompt: str) -> bool:
    math_keywords = [
        "calculate", "add", "subtract", "multiply", "divide", "solve", "equation",
        "plus", "minus", "times", "divided by",
        "+", "-", "*", "/", "=",
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "zero"
    ]
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in math_keywords):
        return True
    if re.search(r"\d", prompt) and re.search(r"[+\-*/=]", prompt):
        return True
    return False

def contains_political_content(text: str) -> bool:
    political_keywords = [
        "president", "prime minister", "government", "election",
        "politics", "party", "minister", "senate", "parliament"
    ]
    pattern = re.compile(r"|".join(political_keywords), re.IGNORECASE)
    return bool(pattern.search(text))

async def run_agent(prompt: str):
    global api_call_count
    if api_call_count >= MAX_API_CALLS:
        print("⚠️ API call limit reached. Please wait before trying again.")
        return

    if not is_math_query(prompt):
        print("⛔ Input blocked: Only math-related questions are allowed.")
        return

    print("✅ Input allowed. Querying OpenAI...")

    system_message = {
        "role": "system",
        "content": "You are a helpful assistant that solves math problems and returns only the final answer."
    }

    try:
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-4o-mini",
            messages=[
                system_message,
                {"role": "user", "content": prompt}
            ]
        )
        api_call_count += 1  # Increment after successful call
    except openai.error.RateLimitError:
        print("❌ Rate limit exceeded. Please check your OpenAI account quota.")
        return
    except Exception as e:
        print(f"❌ API error: {e}")
        return

    assistant_reply = response['choices'][0]['message']['content']

    if contains_political_content(assistant_reply):
        print("⛔ Output blocked: Response contains political content.")
    else:
        print("✅ Agent Response:")
        print(assistant_reply)

if __name__ == "__main__":
    while True:
        user_input = input("Ask a math-related question: ")
        asyncio.run(run_agent(user_input))
