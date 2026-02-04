import anthropic
import base64
import os

# Set Claude API key
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-api03-5uIfHqjUvxwN6nVJykLxR4nzvJQQKcZtH7n6WZEaH2tBO5gZxOjJ9l8g0bK3lQ7BzXvX2BA-gpTrz8f1lLxI8w'

client = anthropic.Anthropic()

# Read the screenshot image
with open('/home/pinky/.openclaw/media/inbound/file_5---f3e36458-39a1-4870-90c7-abb6a77de8df.jpg', 'rb') as img_file:
    image_data = base64.b64encode(img_file.read()).decode('utf-8')

# Analyze image and generate website code
response = client.messages.create(
    model='claude-3-haiku-20240307',
    max_tokens=3000,
    messages=[{
        'role': 'user',
        'content': [
            {
                'type': 'image',
                'source': {
                    'type': 'base64',
                    'media_type': 'image/jpeg',
                    'data': image_data
                }
            },
            {
                'type': 'text',
                'text': '''Analyze this website screenshot and create professional HTML/CSS code to recreate this design exactly.

Focus on:
1. Exact color scheme and gradient backgrounds
2. Typography, fonts, and text hierarchy  
3. Layout structure and spacing
4. Button styling and hover effects
5. Responsive design
6. Modern CSS techniques

Provide complete, clean HTML and CSS files that match this design perfectly.'''
            }
        ]
    }]
)

print(response.content[0].text)