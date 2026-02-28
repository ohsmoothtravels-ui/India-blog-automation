# 🇮🇳 India Travel Blog Automation — Free Setup Guide

Automatically generates AI blog posts about India's unique locations,
publishes them to Blogger, and shares across X, Facebook, Instagram & LinkedIn — **100% free**.

---

## How It Works

```
Every day at 9:30 AM IST
        ↓
GitHub Actions triggers the script
        ↓
Gemini AI writes a blog post about an Indian location
        ↓
Post is published to your Blogger blog
        ↓
Shared automatically to X, Facebook, Instagram & LinkedIn
```

---

## STEP 1 — Set Up Google Gemini API (Free AI)

1. Go to [https://aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API Key"**
4. Copy the key — this is your `GEMINI_API_KEY`

✅ Free tier: 15 requests/minute, 1,500 requests/day — more than enough!

---

## STEP 2 — Set Up Blogger API

### 2a. Enable the API
1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g., "Blog Automation")
3. Go to **APIs & Services → Library**
4. Search **"Blogger API v3"** → Click **Enable**

### 2b. Create OAuth Credentials
1. Go to **APIs & Services → Credentials**
2. Click **"+ Create Credentials" → OAuth 2.0 Client ID**
3. Application type: **Desktop app**
4. Download the JSON file → rename it to **`client_secrets.json`**

### 2c. Get Your Blog ID
1. Go to [https://www.blogger.com](https://www.blogger.com)
2. Open your blog's dashboard
3. Look at the URL: `https://www.blogger.com/blog/posts/YOUR_BLOG_ID_HERE`
4. Copy that number — this is your `BLOGGER_BLOG_ID`

### 2d. Generate the Auth Token (run once on your computer)
1. Install Python from [https://python.org](https://python.org) if you don't have it
2. Put `client_secrets.json` and `generate_token.py` in the same folder
3. Open terminal/command prompt in that folder and run:
   ```bash
   pip install google-auth google-auth-oauthlib google-api-python-client
   python generate_token.py
   ```
4. A browser window opens → log in → allow access
5. Copy the long string printed in the terminal → this is your `BLOGGER_TOKEN_B64`

---

## STEP 3 — Set Up X (Twitter) API (Free)

1. Go to [https://developer.twitter.com](https://developer.twitter.com)
2. Sign in and click **"Sign up for Free Account"**
3. Create a new app → go to **"Keys and Tokens"**
4. Generate and save:
   - `API Key` → `TWITTER_API_KEY`
   - `API Secret` → `TWITTER_API_SECRET`
   - `Access Token` → `TWITTER_ACCESS_TOKEN`
   - `Access Token Secret` → `TWITTER_ACCESS_SECRET`
5. Make sure the app has **Read and Write** permissions

---

## STEP 4 — Set Up Facebook Page API (Free)

> You need a Facebook **Page** (not personal profile) to post via API.

1. Create a Facebook Page if you don't have one (free)
2. Go to [https://developers.facebook.com](https://developers.facebook.com)
3. Create a new app → select **"Business"** type
4. Add the **"Pages API"** product
5. Go to **Graph API Explorer**:
   - Select your app
   - Click **"Generate Access Token"** → select your Page
   - Grant all `pages_manage_posts` and `pages_read_engagement` permissions
6. Copy:
   - Your Page ID → `FACEBOOK_PAGE_ID`
   - The access token → `FACEBOOK_ACCESS_TOKEN`

> ⚠️ For a long-lived token (60 days), follow:
> `https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived`

---

## STEP 5 — Set Up Instagram API (Free)

> Requires an Instagram **Business Account** linked to your Facebook Page.

1. In Instagram app: Settings → Account → **Switch to Professional Account → Business**
2. Link it to your Facebook Page
3. In Facebook Developers, add the **Instagram Graph API** product to your app
4. In Graph API Explorer, get your Instagram account ID:
   ```
   GET /me/accounts → find your page → GET /{page-id}?fields=instagram_business_account
   ```
5. Copy the `id` value → this is your `INSTAGRAM_ACCOUNT_ID`
6. Use the same `FACEBOOK_ACCESS_TOKEN` from Step 4

---

## STEP 6 — Set Up LinkedIn API (Free)

1. Go to [https://www.linkedin.com/developers](https://www.linkedin.com/developers)
2. Create a new app → associate with a LinkedIn Page
3. Request **"Share on LinkedIn"** and **"Sign In with LinkedIn"** products
4. Go to **Auth** tab → generate an access token with `w_member_social` scope
5. Copy:
   - Access token → `LINKEDIN_ACCESS_TOKEN`
   - Your LinkedIn URN (format: `urn:li:person:XXXXXXXX`) → `LINKEDIN_URN`
   - Get your URN by calling: `GET https://api.linkedin.com/v2/me` with your token

---

## STEP 7 — Upload Code to GitHub

1. Log into [https://github.com](https://github.com)
2. Click **"New Repository"** → name it `india-blog-automation` → **Public** → Create
3. Upload these files to the repository:
   - `main.py`
   - `requirements.txt`
   - `.github/workflows/automate.yml`

---

## STEP 8 — Add All Secrets to GitHub

1. In your GitHub repo, go to **Settings → Secrets and Variables → Actions**
2. Click **"New repository secret"** and add each of these:

| Secret Name | Where to Get It |
|---|---|
| `GEMINI_API_KEY` | Step 1 |
| `BLOGGER_BLOG_ID` | Step 2c |
| `BLOGGER_TOKEN_B64` | Step 2d |
| `TWITTER_API_KEY` | Step 3 |
| `TWITTER_API_SECRET` | Step 3 |
| `TWITTER_ACCESS_TOKEN` | Step 3 |
| `TWITTER_ACCESS_SECRET` | Step 3 |
| `FACEBOOK_PAGE_ID` | Step 4 |
| `FACEBOOK_ACCESS_TOKEN` | Step 4 |
| `INSTAGRAM_ACCOUNT_ID` | Step 5 |
| `LINKEDIN_ACCESS_TOKEN` | Step 6 |
| `LINKEDIN_URN` | Step 6 |

---

## STEP 9 — Test It!

1. Go to your GitHub repo → **Actions** tab
2. Click **"Blog Automation — Daily Post"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs — you'll see each step in real time ✅

---

## Schedule

The automation runs **every day at 9:30 AM IST** automatically.
To change the time, edit this line in `automate.yml`:
```yaml
- cron: "0 4 * * *"   # 4:00 UTC = 9:30 AM IST
```
Use [https://crontab.guru](https://crontab.guru) to pick a different time.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Blogger auth fails | Re-run `generate_token.py` and update `BLOGGER_TOKEN_B64` secret |
| Twitter 403 error | Check your app has Read+Write permissions |
| Facebook/Instagram errors | Refresh your access token (they expire in 60 days) |
| LinkedIn 401 error | Generate a new access token from the developer portal |

---

## Cost Summary

| Tool | Cost |
|---|---|
| Gemini API | **Free** (1,500 posts/day limit) |
| Blogger API | **Free** |
| GitHub Actions | **Free** (2,000 min/month) |
| X/Twitter API | **Free** (basic tier) |
| Facebook/Instagram API | **Free** |
| LinkedIn API | **Free** |
| **TOTAL** | **$0/month** |
