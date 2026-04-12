import requests

from config import OPENROUTER_API_KEY


def generate_summary(status):
    try:
        prompt = f"""
        You are an AI monitoring assistant.
        Given the agent status: {status}
        Generate a short one-line health summary.
        """

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            },
            timeout=10,
        )

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        # fallback (VERY IMPORTANT for hackathon safety)
        return f"Status is {status}"
