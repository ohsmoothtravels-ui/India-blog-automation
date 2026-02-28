import os
import json
import random
import requests
import tweepy
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# ─────────────────────────────────────────────
# CONFIGURATION — all values come from GitHub Secrets
# ─────────────────────────────────────────────

GEMINI_API_KEY       = os.environ["GEMINI_API_KEY"]
BLOGGER_BLOG_ID      = os.environ["BLOGGER_BLOG_ID"]

# Twitter / X
TWITTER_API_KEY         = os.environ["TWITTER_API_KEY"]
TWITTER_API_SECRET      = os.environ["TWITTER_API_SECRET"]
TWITTER_ACCESS_TOKEN    = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET   = os.environ["TWITTER_ACCESS_SECRET"]

# Facebook & Instagram (same Graph API)
FACEBOOK_PAGE_ID        = os.environ["FACEBOOK_PAGE_ID"]
FACEBOOK_ACCESS_TOKEN   = os.environ["FACEBOOK_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID    = os.environ["INSTAGRAM_ACCOUNT_ID"]

# LinkedIn
LINKEDIN_ACCESS_TOKEN   = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_URN            = os.environ["LINKEDIN_URN"]   # urn:li:person:XXXXXXXX

# Blogger OAuth token (stored as a secret, base64-encoded pickle)
BLOGGER_TOKEN_B64       = os.environ["BLOGGER_TOKEN_B64"]

# ─────────────────────────────────────────────
# TOPICS — India's unique locations
# ─────────────────────────────────────────────

TOPICS = [
    "Spiti Valley, Himachal Pradesh — the cold desert monastery land",
    "Dzukou Valley, Nagaland — the valley of flowers of the Northeast",
    "Gandikota, Andhra Pradesh — India's hidden Grand Canyon",
    "Gurez Valley, Kashmir — the untouched valley near the LOC",
    "Majuli Island, Assam — the world's largest river island",
    "Ziro Valley, Arunachal Pradesh — the land of the Apatani tribe",
    "Chopta, Uttarakhand — the mini Switzerland of India",
    "Dholavira, Gujarat — the ancient Harappan city",
    "Loktak Lake, Manipur — the lake with floating islands (phumdis)",
    "Unakoti, Tripura — the lost city of rock-cut sculptures",
    "Lambasingi, Andhra Pradesh — the Kashmir of Andhra",
    "Mawlynnong, Meghalaya — Asia's cleanest village",
    "Rann of Kutch, Gujarat — the white salt desert",
    "Hemis National Park, Ladakh — land of the snow leopard",
    "Sandakphu, West Bengal — the only place to see 4 of the world's 5 highest peaks",
    "Bhimashankar, Maharashtra — the misty forest wildlife sanctuary",
    "Lonar Crater Lake, Maharashtra — a meteor crater lake",
    "Champaner-Pavagadh, Gujarat — a UNESCO World Heritage archaeological park",
    "Tawang, Arunachal Pradesh — the land of the sacred monastery",
    "Panchmarhi, Madhya Pradesh — the queen of Satpura",
]

# ─────────────────────────────────────────────
# STEP 1 — Generate blog post using Gemini API
# ─────────────────────────────────────────────

def generate_blog_post(topic: str) -> dict:
    """Call Gemini to write a full blog post. Returns {title, body, summary, hashtags}."""
    print(f"✍️  Generating post about: {topic}")

    prompt = f"""You are a travel blogger writing engaging, SEO-friendly content about India's unique and offbeat destinations.

Write a complete blog post about: {topic}

Return ONLY valid JSON (no markdown, no code fences) in this exact format:
{{
  "title": "An engaging, SEO-friendly blog post title",
  "body": "Full HTML blog post body (use <h2>, <p>, <ul>, <li> tags). Minimum 600 words. Include sections: Introduction, How to Reach, Best Time to Visit, Things to Do, Where to Stay, Travel Tips, Conclusion.",
  "summary": "A 1-2 sentence summary for social media (max 200 characters)",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"]
}}"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 2048}
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    # Strip markdown fences if present
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    post_data = json.loads(raw_text.strip())
    print(f"✅ Generated: {post_data['title']}")
    return post_data

# ─────────────────────────────────────────────
# STEP 2 — Publish to Blogger
# ─────────────────────────────────────────────

def publish_to_blogger(title: str, body: str) -> str:
    """Publish post to Blogger. Returns the live post URL."""
    print("📝 Publishing to Blogger...")

    import base64
    token_bytes = base64.b64decode(BLOGGER_TOKEN_B64)
    creds = pickle.loads(token_bytes)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("blogger", "v3", credentials=creds)

    post = {
        "title": title,
        "content": body,
        "labels": ["India Travel", "Offbeat Destinations", "Explore India"]
    }

    result = service.posts().insert(blogId=BLOGGER_BLOG_ID, body=post, isDraft=False).execute()
    post_url = result.get("url", "")
    print(f"✅ Published to Blogger: {post_url}")
    return post_url

# ─────────────────────────────────────────────
# STEP 3 — Share to X (Twitter)
# ─────────────────────────────────────────────

def share_to_twitter(summary: str, hashtags: list, post_url: str):
    print("🐦 Sharing to X (Twitter)...")
    try:
        tags = " ".join([f"#{h.replace('#','')}" for h in hashtags[:3]])
        tweet = f"{summary}\n\n{tags}\n\n🔗 {post_url}"
        tweet = tweet[:280]  # Twitter limit

        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        client.create_tweet(text=tweet)
        print("✅ Shared to X")
    except Exception as e:
        print(f"❌ Twitter error: {e}")

# ─────────────────────────────────────────────
# STEP 4 — Share to Facebook Page
# ─────────────────────────────────────────────

def share_to_facebook(summary: str, post_url: str):
    print("📘 Sharing to Facebook...")
    try:
        url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed"
        payload = {
            "message": f"🇮🇳 {summary}\n\nRead more 👇",
            "link": post_url,
            "access_token": FACEBOOK_ACCESS_TOKEN
        }
        r = requests.post(url, data=payload)
        r.raise_for_status()
        print("✅ Shared to Facebook")
    except Exception as e:
        print(f"❌ Facebook error: {e}")

# ─────────────────────────────────────────────
# STEP 5 — Share to Instagram (caption only, no image)
# ─────────────────────────────────────────────

def share_to_instagram(summary: str, hashtags: list):
    """
    Instagram requires an image for feed posts.
    We use a free static travel image from Unsplash as the visual.
    """
    print("📸 Sharing to Instagram...")
    try:
        tags = " ".join([f"#{h.replace('#','')}" for h in hashtags])
        caption = f"🇮🇳 {summary}\n\n{tags}\n\n#IndiaTourism #IncredibleIndia #TravelIndia #HiddenGems"

        # Use a free Unsplash India travel image
        image_url = "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1080"

        # Step 1: Create media container
        container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
        container_payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": FACEBOOK_ACCESS_TOKEN
        }
        r = requests.post(container_url, data=container_payload)
        r.raise_for_status()
        container_id = r.json()["id"]

        # Step 2: Publish container
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": FACEBOOK_ACCESS_TOKEN
        }
        r2 = requests.post(publish_url, data=publish_payload)
        r2.raise_for_status()
        print("✅ Shared to Instagram")
    except Exception as e:
        print(f"❌ Instagram error: {e}")

# ─────────────────────────────────────────────
# STEP 6 — Share to LinkedIn
# ─────────────────────────────────────────────

def share_to_linkedin(title: str, summary: str, post_url: str):
    print("💼 Sharing to LinkedIn...")
    try:
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        payload = {
            "author": LINKEDIN_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": f"🇮🇳 {title}\n\n{summary}\n\nRead the full post 👇\n{post_url}\n\n#IndiaTourism #TravelIndia #IncredibleIndia #OffbeatTravel"
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [{
                        "status": "READY",
                        "originalUrl": post_url,
                        "title": {"text": title}
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        print("✅ Shared to LinkedIn")
    except Exception as e:
        print(f"❌ LinkedIn error: {e}")

# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def main():
    print(f"\n🚀 Blog Automation Started — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Pick a random topic
    topic = random.choice(TOPICS)
    print(f"📍 Today's topic: {topic}\n")

    # Step 1: Generate content
    post = generate_blog_post(topic)

    # Step 2: Publish to Blogger
    post_url = publish_to_blogger(post["title"], post["body"])

    # Step 3-6: Share to all social platforms
    share_to_twitter(post["summary"], post["hashtags"], post_url)
    share_to_facebook(post["summary"], post_url)
    share_to_instagram(post["summary"], post["hashtags"])
    share_to_linkedin(post["title"], post["summary"], post_url)

    print(f"\n🎉 All done! Post published and shared across all platforms.\n")
    print(f"📌 Blog URL: {post_url}")

if __name__ == "__main__":
    main()
