# Instagram Automation Bot

This project is an Instagram automation bot designed to perform tasks such as viewing stories, engaging with feed posts, and sending direct messages to new followers. It uses the `instagrapi` library to interact with Instagram's API.

## Features

- **Story Viewing**: Automatically views stories from followed accounts.
- **Feed Engagement**: Likes and comments on posts in the feed.
- **Direct Messaging**: Sends welcome messages to new followers.

## Requirements

- Python 3.8 or higher
- Instagram account credentials

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set your Instagram credentials as environment variables:
- `INSTAGRAM_USERNAME`: Your Instagram username
- `INSTAGRAM_PASSWORD`: Your Instagram password

## Usage

Run the bot using the following command:
```bash
python bot.py
```

The bot will authenticate and start an engagement cycle, which includes viewing stories, engaging with feed posts, and messaging new followers. It will repeat the cycle every 30 minutes.

## Dependencies

The project relies on the following Python packages:
- `instagrapi==2.1.3`
- `pytz==2025.1`
- `requests==2.32.3`
- `pillow==11.1.0`
- `pycryptodomex==3.21.0`
- `pydantic==2.10.1`
- `PySocks==1.7.1`
- `urllib3==2.3.0`
- `certifi==2025.1.31`
- `charset-normalizer==3.4.1`
- `idna==3.10`
- `typing_extensions==4.12.2`
- `annotated-types==0.7.0`
- `pydantic_core==2.27.1`

## License

This project is licensed under the MIT License.

## Disclaimer

This bot is intended for educational purposes only. Use it responsibly and ensure compliance with Instagram's terms of service. 