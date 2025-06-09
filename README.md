# Games Playing Minicraft Snakes

<img src = "snake playing.mp4.gif" width = "100%" height ="100%">

# Complete Installation Guide for Python in Termux

<img src = "snake.png" width = "300" height = "300">

## Initial Setup

1. Install Termux from F-Droid store (recommended) or Google Play Store

2. Launch Termux and update the system:
```bash
apt update && apt upgrade -y
```

3. Setup storage access:
```bash
termux-setup-storage
```

## Required Packages Installation

4. Install essential packages:
```bash
pkg install python -y
pkg install python-pip -y
pkg install git -y
pkg install nano -y
```

5. Install Python dependencies:
```bash
pip install --upgrade pip
pip install requests
pip install pillow
pip install bs4
```

## Script Setup & Execution

6. Navigate to your working directory:
```bash
cd /sdcard/your/directory
```

7. Set proper permissions:
```bash
chmod +x main.py
```

8. Run your script:
```bash
python main.py
```

## Troubleshooting

- Permission denied error: Run `termux-setup-storage`
- Pip installation fails: Try `pkg install python-pip`
- Package conflicts: Run `pip install --upgrade package_name`
- Storage access issues: Verify Android permissions for Termux

**Note:**
- Always run updates periodically
- Keep Python and pip updated
- Check internet connectivity for installations
