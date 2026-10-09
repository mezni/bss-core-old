
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

if not api_key or not model:
    raise RuntimeError(
        "Set OPENAI_API_KEY and OPENAI_MODEL in your .env file."
    )

client = OpenAI(api_key=api_key)

ticket = """
My order #4821 has not arrived.
It was supposed to arrive three days ago.
Can you check the status?
"""

instructions = """
You are a customer support ticket analyzer.

Classify the ticket and draft a concise response.
Do not invent an order status or claim to have checked a database.

Return:
1. Category
2. Priority
3. Order ID, if present
4. Draft reply
"""

start = time.perf_counter()

response = client.responses.create(
    model=model,
    instructions=instructions,
    input=ticket,
    max_output_tokens=200,
)

elapsed_seconds = time.perf_counter() - start

print("MODEL:", model)
print("\nRESPONSE:")
print(response.output_text)

print("\nMETRICS:")
print("Latency (seconds):", round(elapsed_seconds, 3))

if response.usage:
    print("Input tokens:", response.usage.input_tokens)
    print("Output tokens:", response.usage.output_tokens)
