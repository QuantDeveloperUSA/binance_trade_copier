# SSH Configuration for VPS Access

This directory contains SSH configuration files for connecting to the remote VPS.

## Files Overview

- `ssh_config` - SSH client configuration file
- `vps_key.pub` - Public key (safe to share/commit)
- `setup_instructions.md` - Instructions for setting up SSH key authentication

## Quick Connection

After setting up the SSH keys locally, you can connect using:

```bash
# Using the config file
ssh -F ssh_config/ssh_config vps

# Or using the full command
ssh -i ~/.ssh/vps_key trader@5.181.5.168
```

## Setup Instructions

1. **Generate SSH Key Pair** (if not already done):
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/vps_key
   ```

2. **Copy Public Key to VPS**:
   ```bash
   scp ~/.ssh/vps_key.pub trader@5.181.5.168:~/
   ```

3. **On the VPS, add the key to authorized_keys**:
   ```bash
   # For regular users
   cat ~/vps_key.pub >> ~/.ssh/authorized_keys
   
   # For admin users (Windows VPS)
   copy vps_key.pub C:\ProgramData\ssh\administrators_authorized_keys
   ```

4. **Test the connection**:
   ```bash
   ssh -i ~/.ssh/vps_key trader@5.181.5.168
   ```

## Security Notes

- **NEVER commit private keys to git**
- The private key (`vps_key`) should remain in your local `~/.ssh/` directory
- Only the public key (`vps_key.pub`) is safe to share and commit
- Make sure your `.gitignore` includes private key patterns

## VPS Details

- **Host**: 5.181.5.168
- **User**: trader
- **Authentication**: SSH Key (recommended) or Password
- **OS**: Windows Server
