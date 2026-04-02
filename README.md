# Windsurf Quota Checker

A Python automation tool that logs into your Windsurf account and retrieves your usage quota information.

## Features

- Automated login to Windsurf account
- Extracts daily quota percentage
- Extracts weekly quota percentage
- Retrieves extra usage balance
- Secure credential management using environment variables
- Session persistence (saves cookies and storage data)

**Note:** Due to Windsurf's security measures, sessions may expire quickly between runs. The script will automatically re-login when needed, so you still get fully automated quota checking without manual intervention.

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed
- Internet connection

## Installation

1. Clone or download this project

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Setup Guide

### Step 1: Configure Your Credentials

1. Copy the example environment file:
   - Rename `.env.example` to `.env`

2. Edit the `.env` file and add your Windsurf credentials:
   ```
   WINDSURF_EMAIL=your_email@example.com
   WINDSURF_PASSWORD=your_password_here
   ```

   **Important:** 
   - Replace `your_email@example.com` with your actual Windsurf email
   - Replace `your_password_here` with your actual Windsurf password
   - The `.env` file is already in `.gitignore` to keep your credentials safe

### Step 2: Run the Script

Execute the main script:
```bash
python windsurf_quota.py
```

The script will:
1. Open a Chrome browser window
2. Navigate to the Windsurf login page
3. Automatically enter your credentials and log in
4. Navigate to the usage page
5. Extract and display your quota information
6. Close the browser

## Output Example

```
==================================================
WINDSURF QUOTA INFORMATION
==================================================
Your daily quota: 71.00% remaining
Your weekly quota: 0.00% remaining
Extra usage balance available: $28.31
==================================================
```

## Headless Mode

To run the script without opening a visible browser window, modify the last line in `windsurf_quota.py`:

```python
checker.run(headless=True)  # Change False to True
```

## Troubleshooting

### Login Issues
- Verify your credentials in the `.env` file are correct
- Check if Windsurf has changed their login page structure
- The script will save a screenshot (`error_screenshot.png`) if an error occurs

### Quota Information Not Found
- The script tries multiple methods to extract quota data
- If the page structure has changed, you may need to update the selectors
- Check `quota_page_error.png` for debugging

### ChromeDriver Issues
- The script automatically downloads the correct ChromeDriver version
- Ensure you have Google Chrome installed
- Check your internet connection

## Security Notes

- Never commit your `.env` file to version control
- Keep your credentials secure
- The `.gitignore` file is configured to exclude `.env` automatically

## Project Structure

```
windsurf_api/
├── windsurf_quota.py    # Main script
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment file
├── .env               # Your credentials (create this)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Dependencies

- **selenium**: Web automation framework
- **webdriver-manager**: Automatic ChromeDriver management
- **python-dotenv**: Environment variable management

## License

This project is provided as-is for personal use.
