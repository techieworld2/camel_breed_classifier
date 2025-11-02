#!/bin/bash

# Git LFS Setup Script for Camel Classifier
echo "🚀 Setting up Git LFS for model file..."

# Check if Git LFS is installed
if ! command -v git-lfs &> /dev/null; then
    echo "❌ Git LFS not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y git-lfs
fi

# Initialize Git LFS
git lfs install

# Track .pt files with LFS
git lfs track "*.pt"

# Add gitattributes
git add .gitattributes

# Add model file
git add fastapi_backend/best_model.pt

echo "✅ Git LFS configured!"
echo ""
echo "Next steps:"
echo "1. git commit -m 'Add model with Git LFS'"
echo "2. git push"
echo ""
echo "Your 44MB model file will now be handled by Git LFS!"
