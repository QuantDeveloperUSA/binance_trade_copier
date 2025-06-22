#!/bin/bash
# SSH Key Setup Script for GitHub Actions Deployment
# Run this on your local machine (Linux/Mac/WSL)

echo "=========================================="
echo "  SSH Key Setup for GitHub Actions"
echo "=========================================="
echo

# Configuration
VPS_HOST="5.181.5.168"
VPS_USER="trader"
KEY_NAME="id_rsa_vps_deploy"

echo "This script will help you set up SSH keys for automated deployment."
echo "VPS Host: $VPS_HOST"
echo "VPS User: $VPS_USER"
echo

# Check if ssh-keygen exists
if ! command -v ssh-keygen &> /dev/null; then
    echo "ERROR: ssh-keygen not found. Please install OpenSSH client."
    exit 1
fi

# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Generate SSH key pair
echo "Step 1: Generating SSH key pair..."
if [ -f ~/.ssh/$KEY_NAME ]; then
    echo "Warning: Key file ~/.ssh/$KEY_NAME already exists!"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Exiting without generating new key."
        exit 1
    fi
fi

ssh-keygen -t rsa -b 4096 -C "github-actions-deploy-$(date +%Y%m%d)" -f ~/.ssh/$KEY_NAME -N ""

if [ $? -eq 0 ]; then
    echo "✅ SSH key pair generated successfully!"
    echo "   Private key: ~/.ssh/$KEY_NAME"
    echo "   Public key: ~/.ssh/${KEY_NAME}.pub"
else
    echo "❌ Failed to generate SSH key pair."
    exit 1
fi

echo
echo "Step 2: Public key content (copy this to your VPS):"
echo "----------------------------------------"
cat ~/.ssh/${KEY_NAME}.pub
echo "----------------------------------------"
echo

echo "Step 3: Private key content for GitHub secrets:"
echo "Copy the following content to GitHub repository secrets as 'VPS_SSH_KEY':"
echo "----------------------------------------"
cat ~/.ssh/$KEY_NAME
echo "----------------------------------------"
echo

echo "Step 4: VPS Configuration Commands:"
echo "Run these commands on your Windows VPS:"
echo "----------------------------------------"
echo "mkdir C:\\Users\\$VPS_USER\\.ssh"
echo "# Then add the public key content to:"
echo "# C:\\Users\\$VPS_USER\\.ssh\\authorized_keys"
echo "----------------------------------------"
echo

echo "Step 5: Test SSH connection:"
echo "ssh -i ~/.ssh/$KEY_NAME $VPS_USER@$VPS_HOST"
echo

echo "Step 6: GitHub Repository Secrets:"
echo "Go to your GitHub repository > Settings > Secrets and variables > Actions"
echo "Add a new secret:"
echo "  Name: VPS_SSH_KEY"
echo "  Value: [paste the private key content from above]"
echo

echo "Setup complete! Test the SSH connection before pushing to main branch."
