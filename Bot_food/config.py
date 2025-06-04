from dotenv import load_dotenv
import os

load_dotenv()

ADMINS = list(map(int, os.getenv("ADMINS", "").split(",")))

CHAT_ID_GENERAL = int(os.getenv("CHAT_ID_GENERAL"))
CHAT_ID_OFFICE_COURIER = int(os.getenv("CHAT_ID_OFFICE_COURIER"))
CHAT_ID_KSE = int(os.getenv("CHAT_ID_KSE"))


CHAT_IDS = {
    "офисный курьер": CHAT_ID_OFFICE_COURIER,
    "курьерская служба": CHAT_ID_KSE,
}
