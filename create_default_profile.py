import os
from PIL import Image, ImageDraw, ImageFont

# Create uploads directory if it doesn't exist
uploads_dir = os.path.join('static', 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

# Create a default profile image
def create_default_profile_image(username):
    # Create a blank image
    img = Image.new('RGB', (500, 500), color='#3498db')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 200)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw the first letter of the username
    first_letter = username[0].upper() if username else 'U'
    
    # Get text size
    bbox = draw.textbbox((0, 0), first_letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center the text
    position = ((500-text_width)/2, (500-text_height)/2)
    
    # Draw text in white
    draw.text(position, first_letter, fill='white', font=font)
    
    # Save the image
    img_path = os.path.join(uploads_dir, 'default_profile.png')
    img.save(img_path)
    return img_path

# Create a default profile image
create_default_profile_image('User')
print("Default profile image created successfully.")
