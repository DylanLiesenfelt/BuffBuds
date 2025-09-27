from app.config import Config
from supabase import create_client, Client

URL = Config.SUPABASE_URL
KEY = Config.SUPABASE_KEY
supabase: Client = create_client(URL, KEY)
