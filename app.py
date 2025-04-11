import os
import io
import requests
from PIL import Image
import tweepy
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()



# Twitter API credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Hugging Face API credentials
HUGGINGFACE_API_TOKEN = os.getenv("api_key")
HUGGINGFACE_MODEL = "runwayml/stable-diffusion-v1-5"



# Check for missing API keys
def check_api_keys():
    missing_keys = []
    if not TWITTER_API_KEY: missing_keys.append("TWITTER_API_KEY")
    if not TWITTER_API_SECRET: missing_keys.append("TWITTER_API_SECRET")
    if not TWITTER_ACCESS_TOKEN: missing_keys.append("TWITTER_ACCESS_TOKEN")
    if not TWITTER_ACCESS_TOKEN_SECRET: missing_keys.append("TWITTER_ACCESS_TOKEN_SECRET")
    if not HUGGINGFACE_API_TOKEN: missing_keys.append("HUGGINGFACE_API_TOKEN")

    if missing_keys:
        raise ValueError(f"Missing API keys: {', '.join(missing_keys)}. Check your .env file.")


class TextToImageTwitterBot:
    def __init__(self):
        check_api_keys()

        # Initialize Twitter client
        self.twitter_client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )

        # Initialize Twitter API v1.1 for media upload
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET
        )
        self.twitter_api = tweepy.API(auth)

    def generate_image(self, prompt):
        """Generate an image using Stable Diffusion via Hugging Face API"""
        try:
            headers = {
                "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {"inputs": prompt}
            url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            else:
                print(f"Error generating image: {response.status_code} {response.text}")
                return None
        except Exception as e:
            print(f"Error generating image: {e}")
            return None

    def save_image(self, image, filename="generated_image.png"):
        """Save image to file"""
        try:
            image.save(filename)
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None

    def post_to_twitter(self, image_path, tweet_text):
        """Post the image to Twitter with the given text"""
        try:
            media = self.twitter_api.media_upload(image_path)
            media_id = media.media_id
            response = self.twitter_client.create_tweet(text=tweet_text, media_ids=[media_id])
            print(f"Tweet posted successfully! ID: {response.data['id']}")
            return response.data['id']
        except Exception as e:
            print(f"Error posting to Twitter: {e}")
            return None

    def generate_and_post(self, prompt, tweet_text=None):
        """Generate an image from prompt and post to Twitter"""
        if not tweet_text:
            tweet_text = f"AI generated image based on: {prompt}"

        print(f"Generating image for prompt: {prompt}")
        image = self.generate_image(prompt)

        if image:
            print("Image generated successfully")
            image_path = self.save_image(image)
            if image_path:
                tweet_id = self.post_to_twitter(image_path, tweet_text)
                return tweet_id

        return None


def main():
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
HUGGINGFACE_API_TOKEN=your_huggingface_api_token
""")
        print("Created .env file template. Please fill in your API keys.")
        return

    bot = TextToImageTwitterBot()
    prompt = input("Enter text prompt for image generation: ")
    tweet_text = input("Enter tweet text (leave blank to use default): ") or None
    tweet_id = bot.generate_and_post(prompt, tweet_text)

    if tweet_id:
        print(f"Success! Tweet URL: https://twitter.com/user/status/{tweet_id}")
    else:
        print("Failed to generate and post image.")


if __name__ == "__main__":
    main()
