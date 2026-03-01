from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_token(email, token_json):
    supabase.table("users_tokens").upsert({
        "email": email,
        "token": token_json
    }).execute()


def get_token(email):
    response = supabase.table("users_tokens") \
        .select("token") \
        .eq("email", email) \
        .execute()

    if response.data:
        return response.data[0]["token"]

    return None