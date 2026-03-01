from supabase import create_client
import streamlit as st
import json

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_token(email, token_json):
    response = supabase.table("users_tokens").upsert(
        {
            "email": email,
            "token": json.dumps(token_json)
        },
        on_conflict="email"
    ).execute()

    return response

def get_token(email):
    response = supabase.table("users_tokens") \
        .select("token") \
        .eq("email", email) \
        .execute()

    if response.data:
        return json.loads(response.data[0]["token"])

    return None