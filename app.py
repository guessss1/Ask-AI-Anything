from flask import Flask, render_template, request, jsonify
import os
import openai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_internet(query):
    url = "https://api.tavily.com/search"
    params = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "num_results": 5
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print(f"Error during search: {e}")
        return []


def generate_ai_response(question, search_results):
    # Prepare context from search results
    context = "\n".join([f"Source: {result['title']}\nContent: {result['content']}"
                         for result in search_results])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if you prefer
            messages=[
                {"role": "system",
                 "content": "You are an AI search assistant. Use the provided search results to give accurate and informative answers. Always cite sources when possible."},
                {"role": "user", "content": f"Question: {question}\n\nSearch Results:\n{context}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error during AI response generation: {e}")
        return "Sorry, I encountered an error while processing your request."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    question = data.get("question", "")

    # Get search results
    search_results = search_internet(question)

    # Generate AI response
    ai_response = generate_ai_response(question, search_results)

    return jsonify({
        "response": ai_response,
        "search_results": search_results
    })


if __name__ == "__main__":
    app.run(debug=True)