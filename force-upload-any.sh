#!/bin/bash
DEFAULT_PORT=/dev/cu.usbmodem313371

# Check if app directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <app_directory> [port]"
    echo "Example: $0 doom"
    echo "Example: $0 northstar_agy /dev/cu.usbmodem313371"
    exit 1
fi

APP_DIR="$1"
PORT="${2:-$DEFAULT_PORT}"

echo "=== Force uploading $APP_DIR to $PORT ==="

# Check if app directory exists
if [ ! -d "apps/$APP_DIR" ]; then
    echo "Error: apps/$APP_DIR directory does not exist!"
    exit 1
fi

echo "Step 1: Deleting existing files and directories..."
# Delete entire app directory to force clean install
python3 -m mpremote connect port:$PORT fs rmdir :apps/$APP_DIR 2>/dev/null
python3 -m mpremote connect port:$PORT fs rmdir :None/$APP_DIR 2>/dev/null

echo "Step 2: Creating directories..."
python3 -m mpremote connect port:$PORT fs mkdir :apps 2>/dev/null
python3 -m mpremote connect port:$PORT fs mkdir :apps/$APP_DIR 2>/dev/null

echo "Step 3: Uploading fresh files..."
for file in apps/$APP_DIR/*; do
  if [ -f "$file" ]; then
    echo "Uploading file: $file..."
    python3 -m mpremote connect port:$PORT fs cp "$file" :"$file" || exit 1
  elif [ -d "$file" ] && [[ ! "$file" == *"__pycache__"* ]]; then
    echo "Uploading directory: $file..."
    python3 -m mpremote connect port:$PORT fs cp -r "$file" :"$file" || exit 1
  else
    echo "Skipping: $file"
  fi
done

echo "Step 4: Setting up app metadata..."
python3 -m mpremote connect port:$PORT fs mkdir :None 2>/dev/null
python3 -m mpremote connect port:$PORT fs mkdir :None/$APP_DIR 2>/dev/null

# Copy icon and metadata if they exist
if [ -f "apps/$APP_DIR/icon.py" ]; then
    python3 -m mpremote connect port:$PORT fs cp "apps/$APP_DIR/icon.py" ":None/$APP_DIR/icon.py"
fi
if [ -f "apps/$APP_DIR/metadata.json" ]; then
    python3 -m mpremote connect port:$PORT fs cp "apps/$APP_DIR/metadata.json" ":None/$APP_DIR/metadata.json"
fi

echo "Step 5: Listing files to verify..."
python3 -m mpremote connect port:$PORT fs ls ":apps/$APP_DIR/"

echo "✓ Force upload of $APP_DIR complete!"