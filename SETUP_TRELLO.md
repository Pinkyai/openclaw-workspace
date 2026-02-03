# Trello Setup for Our Todo List

## Step 1: Get Trello API Keys
1. Go to: https://trello.com/app-key
2. Copy your API Key
3. Click "Token" link on that page to generate a token
4. Save both somewhere safe

## Step 2: Set Environment Variables
Once you have the keys, run:
```bash
export TRELLO_API_KEY="your-api-key-here"
export TRELLO_TOKEN="your-token-here"
```

## Step 3: Create Our Shared Board
We can create a board called "Sebastian & Pinky Projects" or whatever you prefer

## Step 4: Test It
```bash
# List your boards
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

## Obsidian Setup
- AppImage downloaded to: ~/obsidian.AppImage
- CLI tool: obsidian-cli (working)
- You can run: `./obsidian.AppImage` to start Obsidian
- We'll create a vault for our projects and tasks

Ready when you are! 🐙