# Deploying Quatrro to AWS EC2

This guide walks you through deploying the application to an AWS VM (Ubuntu) using your existing `.ppk` key.

## 1. Convert PPK to PEM (Mac)

Since you are on macOS, you need a `.pem` file to connect via the terminal. You can convert your `.ppk` using `puttygen`.

1.  **Install tools**:
    ```bash
    brew install putty
    ```

2.  **Convert Key**:
    ```bash
    puttygen your-key-file.ppk -O private-openssh -o my-key.pem
    puttygen UbuntuJan2026.ppk -O private-openssh -o my-key.pem
    ```

3.  **Set Permissions** (Critical Step):
    ```bash
    chmod 400 my-key.pem
    ```

## 2. Prepare the Server

1.  **Connect to your VM**:
    ```bash
    ssh -i my-key.pem ubuntu@35.81.184.168
    ```

2.  **Verify connection**: You should see the ubuntu terminal prompt. Type `exit` to return to your local machine for the transfer step.

## 3. Transfer Files

Copy your project files to the server using `scp`. Run this command from your local `quatrro` project folder:

```bash
# Use rsync to copy files (skipping venv, git, etc.) is much faster!
rsync -avz -e "ssh -i my-key.pem" --exclude 'venv' --exclude '__pycache__' --exclude '.git' --exclude 'logs' . ubuntu@35.81.184.168:~/quatrro/
```

*Alternatively, if you prefer zip:*
```bash
# Zip locally (excluding venv)
zip -r app.zip . -x "venv/*" -x ".git/*" -x "__pycache__/*"
# Upload zip
scp -i my-key.pem app.zip ubuntu@35.81.184.168:~/
# On server: unzip app.zip -d quatrro
```

## 4. Final Setup on VM

1.  **SSH back into the VM**:
    ```bash
    ssh -i my-key.pem ubuntu@<your-vm-ip-address>
    ```

2.  **Create .env file**:
    ```bash
    cd quatrro
    nano .env
    ```
    Paste your `GOOGLE_API_KEY=...` content here. Save with `Ctrl+O`, `Enter`, `Ctrl+X`.

3.  **Run the Setup Script**:
    ```bash
    chmod +x scripts/setup_vm.sh
    ./scripts/setup_vm.sh
    ```

    This script will:
    - Install Python & Dependencies.
    - Set up the background service.
    - Start the application.

## 5. Verify & Monitor

-   **Check Status**:
    ```bash
    sudo systemctl status quatrro
    ```

-   **View Logs**:
    ```bash
    # View live logs
    journalctl -u quatrro -f
    ```

## 6. Access the App

Ensure your AWS Security Group ("Firewall") allows **Inbound Traffic** on port **8000** (Custom TCP).

Visit: `http://35.81.184.168:8000`
