from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def get_gpt_explanation(sensor_id, hydrogen_ppm, temperature, humidity):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "⚠️ AI unavailable — GROQ_API_KEY not found in .env"
    
    client = Groq(api_key=api_key)
    prompt = f"""
    Sensor {sensor_id} reports:
    - Hydrogen: {hydrogen_ppm} ppm
    - Temperature: {temperature}°C
    - Humidity: {humidity}%
    A machine learning model flagged this as anomalous.
    In 2-3 sentences, explain what this might mean and suggest a simple operator action.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI unavailable — {str(e)}"
