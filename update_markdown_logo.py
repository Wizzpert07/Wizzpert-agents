import os

# Path to the logo
LOGO_PATH = "wizzpert-plugins/assets/logo.png"

# Markdown banner to insert
LOGO_MARKDOWN = f"![Wizzpert Logo]({LOGO_PATH})\n\n"

# Directory to scan for markdown files
DIRECTORY = "."

def add_logo_to_markdown(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:  # Explicitly set encoding to UTF-8
            content = file.read()
        
        # Check if the logo is already present
        if LOGO_PATH in content:
            print(f"Logo already present in {file_path}")
            return
        
        # Add the logo at the top
        with open(file_path, "w", encoding="utf-8") as file:  # Explicitly set encoding to UTF-8
            file.write(LOGO_MARKDOWN + content)
            print(f"Logo added to {file_path}")
    except UnicodeDecodeError as e:
        print(f"Error reading file {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error with file {file_path}: {e}")

def scan_and_update_markdown_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                add_logo_to_markdown(file_path)

# Run the script
scan_and_update_markdown_files(DIRECTORY)