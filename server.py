from flask import Flask, request, jsonify, send_file, render_template
import os
from app import TextToImageTwitterBot
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt')
        tweet_text = data.get('tweet_text')

        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400

        logger.info(f"Generating image for prompt: {prompt}")

        # Initialize the Twitter bot
        bot = TextToImageTwitterBot()

        # Generate image and save it with a unique filename
        import uuid
        filename = f"{uuid.uuid4()}.png"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Generate the image
        image = bot.generate_image(prompt)
        if not image:
            return jsonify({'success': False, 'error': 'Failed to generate image'}), 500

        # Save the image
        image.save(image_path)

        # Post to Twitter
        tweet_id = bot.post_to_twitter(image_path, tweet_text or f"AI generated image based on: {prompt}")

        if not tweet_id:
            return jsonify({'success': False, 'error': 'Failed to post to Twitter'}), 500

        # Return success response with image URL and tweet ID
        return jsonify({
            'success': True,
            'image_url': f"/static/images/{filename}",
            'tweet_id': tweet_id
        })

    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)