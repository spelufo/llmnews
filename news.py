import requests
import json
import glob
import time
import os
from datetime import datetime, timedelta
import openai
from pydantic import BaseModel
from typing import List




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

class StoryIds(BaseModel):
    story_ids: List[int]


def prompt_system():
    return """
You must filter the list of stories, keeping only the ones about ML, AI or LLMs.

Each story is given as a YAML object like this:

- id: 123456
  score: 100
  title: "GPT-3: Language Models are Few-Shot Learners"
  url: "https://github.com/openai/gpt-3"
  by: "openai"

"""

def prompt_user(stories):
    return "\n".join(prompt_story(story) for story in stories)

def prompt_story(story):
    s = f"- id: {story['id']}\n"
    for k in ["score", "title", "url", "by"]:
        s += f"  {k}: {json.dumps(story.get(k, ''))}\n"
    return s

def filter_stories(stories):
    clean_stories = []
    for story in stories:
        if "url" in story and "id" in story:
            clean_stories.append({
                k: v for k, v in story.items()
                if k in ["id", "score", "title", "url", "by"]
            })
    system_prompt = prompt_system()
    user_prompt = prompt_user(clean_stories)
    completion = openai.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=StoryIds,
    )
    ids = completion.choices[0].message.parsed.story_ids
    return [story for story in stories if story["id"] in ids]

if __name__ == "__main__":
    stories = get_today_stories()
    stories.sort(key=lambda x: x['score'], reverse=True)
    filtered_stories = filter_stories(stories)
    print(prompt_user(filtered_stories))


