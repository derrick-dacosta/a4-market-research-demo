#!/usr/bin/env python3

import os
import sys
import threading
import itertools
import time
from dotenv import load_dotenv
from anthropic import Anthropic
from tavily import TavilyClient

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_news(query: str, tavily: TavilyClient) -> list:
    """Search for recent news articles using Tavily API"""
    response = tavily.search(
        query=query,
        search_depth="basic",
        max_results=5,
        include_raw_content=False,
    )
    return response.get("results", [])


def format_articles(articles: list) -> str:
    """Format articles for Claude to analyze"""
    formatted = []
    for i, article in enumerate(articles, 1):
        formatted.append(
            f"Article {i}:\n"
            f"Title: {article.get('title', 'N/A')}\n"
            f"Source: {article.get('url', 'N/A')}\n"
            f"Content: {article.get('content', 'N/A')}\n"
        )
    return "\n---\n".join(formatted)


class Spinner:
    def __init__(self, message="Researching..."):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.message = message
        self.running = False
        self.thread = None

    def spin(self):
        while self.running:
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 3) + "\r")
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


SYSTEM_PROMPT = """
You are a market research analyst. Your task is to:
    1. Analyze and summarize the key findings from the provided news articles.
    2. Provide a concise market research summary that answers the user's question.

    Focus on recent news and relevant business information. DO NOT select more than 3 articles.
    Always cite your sources by mentioning the article titles or sources.
"""


def research(user_query: str, anthropic: Anthropic, tavily: TavilyClient, conversation: list) -> str:
    """Perform market research and summarization based on user query"""
    articles = search_news(user_query, tavily)

    if articles:
        formatted_articles = format_articles(articles)
        prompt = f"""User's Question: {user_query}

Recent Articles:
{formatted_articles}"""
    else:
        prompt = user_query

    conversation.append({"role": "user", "content": prompt})
    print(f"\nFull Input Prompt -\n{prompt}")

    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=conversation,
    )

    assistant_response = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_response})

    return assistant_response


def main():
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not set in .env")
        return

    if not TAVILY_API_KEY:
        print("Error: TAVILY_API_KEY not set in .env")
        return

    print("Market Research Tool")
    print("=" * 42)
    print("\nEnter your question (or 'quit' to exit):\n")

    anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    conversation = []

    while True:
        try:
            user_input = input("> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("So long and thanks for all the fish!")
                break

            spinner = Spinner("Researching...")
            spinner.start()
            try:
                result = research(user_input, anthropic, tavily, conversation)
            finally:
                spinner.stop()
            print("=" * 42)
            print("LLM RESPONSE")
            print("=" * 42)
            print(result)
            print("=" * 42 + "\n")

        except KeyboardInterrupt:
            print("\nSo long and thanks for all the fish!")
            break


if __name__ == "__main__":
    main()
