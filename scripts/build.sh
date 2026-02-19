#!/bin/bash

echo "Generating tag pages..."
python scripts/generate_tag_pages.py

echo "Building Jekyll site..."
bundle exec jekyll build

echo "Build complete!" 