import requests
import json
import glob
import time
import os
from datetime import datetime, timedelta
import openai

# TODO:
# - Improve input and output formats. Maybe use structured outputs.
# - How much does it cost/day?
# - Generate html.
# - Make a simple web app around it.
# - Release it and try charging for it with stripe.


def fetch_today_stories():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)
    story_ids = response.json()
    a_day_ago = (datetime.now() - timedelta(days=1)).timestamp()
    # There are about 50 top stories per day. The topstories.json isn't ordered strictly by time,
    # but it does roughly go from newest to oldest, and looking at double the number we expect per day
    # should get us all of the top stories for today with high probability.
    peek_stories = 100
    for story_id in story_ids[:peek_stories]:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story_response = requests.get(story_url)
        story = story_response.json()
        if story['time'] < a_day_ago:
            continue
        yield story

def get_today_stories():
    filename = f"stories_{datetime.now().strftime('%Y-%m-%d')}.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        stories = []
        for story in fetch_today_stories():
            stories.append(story)
        json.dump(stories, open(filename, "w"))
        return stories

def filter_stories(stories):
    story_lines = ""
    for story in stories:
        story_lines += f"{story['score']}\t{story['title']} ({story.get('url', '')})\n"
    message = f"Filter this list to keep only the articles that have to do with AI or LLMs:\n\n{story_lines}"
    response = openai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": message}])
    return response.choices[0].message.content

if __name__ == "__main__":
    stories = get_today_stories()
    stories.sort(key=lambda x: x['score'], reverse=True)
    response = filter_stories(stories)
    print(response)



