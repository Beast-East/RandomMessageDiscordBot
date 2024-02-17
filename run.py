from bot_main import Bot
from dotenv import load_dotenv
import os

# Load .env file to get the BOT_TOKEN
script_dir = os.path.dirname(os.path.realpath(__file__))
env_file_path = os.path.join(script_dir, '.env')
load_dotenv(env_file_path)


def main():
    token = str(os.environ.get("BOT_TOKEN"))
    bot1 = Bot(token)
    bot1.run_bot()


if __name__ == "__main__":
    main()
