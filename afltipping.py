import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from smolagents import tool, ToolCallingAgent, DuckDuckGoSearchTool, GoogleSearchTool, LiteLLMModel
from tools.odds_download_tool import odds_download_tool

def chunk_response(text, max_length=2000) -> list[str]:
    """  Splits a string into chunks of a maximum length, preferably at newlines.

    Args:
        text: The string to split
        max_length: The max length of each chunk (default: 2000)

    Returns:
        A list of strings
    """
    chunks = []
    current_chunk = ""

    for line in text.splitlines(keepends=True):
        if len(current_chunk) + len(line) <= max_length:
            current_chunk += line
        else:
            chunks.append(current_chunk)
            current_chunk = line

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def create_predictions():
    try:

        model = LiteLLMModel(model_id="gpt-4o-mini")
        agent = ToolCallingAgent(tools=[DuckDuckGoSearchTool(), odds_download_tool], model=model, add_base_tools=True, planning_interval=5, max_steps=20)
        date = datetime.now().strftime("%Y-%m-%d")
        
        query = f"""Today is {date} (YYYY-MM-DD). Predict what teams are most likely to win this week's round of AFL
        matches (rounds typically run Thurs-Sun), first use odds_download_tool to get a list of matches and current odds,
        using the commence_time in the response work out the current round and then also search for commentator and 
        public opinion on the matches (verify current round and season when performing serches - remember AFL's opening
        round is round 0). Please give a brief summary of opinion with each prediction and write in the style of
        Warwick Capper with plenty of personality. Please predict the same number of matches listed in the odds_download_tool -
        make sure to include each match listed from the download tool and the team you predict to win. If there are no
        matches this week please state that there are no matches this week and provide a brief summary of the current
        season status and any interesting news or events in the AFL world.
        Don't  mention the name Warwick Capper and provide a concise final answer in format: 
        Intro [**Match** - Odds\\nSummary\\nPrediction] Outro"""

        response = agent.run(query)

        #response = "Test"
        if response is not None:

            response_chunks = chunk_response(response)

            for chunk in response_chunks:
                data = {"content": str(chunk)}
                
                if os.environ.get('DISCORD_WEBHOOK') is not None:
                    requests.post(os.environ.get('DISCORD_WEBHOOK'), json=data, timeout=5)

            print(response)
        else:
            raise Exception("No response")

    except Exception as e: 
        error = {"content": str(e)}
        if os.environ.get('DISCORD_DEBUG_WEBHOOK') is not None:
            requests.post(os.environ.get('DISCORD_DEBUG_WEBHOOK'), json=error, timeout=3)

        print(e)

def handler(event, context):
    """ Handler to run in AWS lambdas"""
    create_predictions()

if __name__ == "__main__":
    create_predictions()
