# Import required libraries
from dotenv import load_dotenv
load_dotenv()   # Load environment variables from .env file
from supabase import create_client, Client
import os # Import os module for accessing environment variables

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASEc_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Print the Supabase URL from environment variables to verify connection
print("Supabase URL:", os.getenv("SUPABASE_URL"))
