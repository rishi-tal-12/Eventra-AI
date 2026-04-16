# Instagram Graph API Setup Guide

## Prerequisites
You CANNOT use this system without these — no shortcuts exist.

### 1. Business/Creator Account
- Go to Instagram → Settings → Account → Switch to Professional Account
- Choose **Creator** (for personal/student use) or **Business**
- Creator accounts now support Content Publishing API ✓

### 2. Facebook Page
- Instagram Business API routes through Facebook's infrastructure
- Create a Facebook Page (doesn't need followers)
- Link it: Instagram → Settings → Linked Accounts → Facebook

### 3. Meta Developer Account
- Go to https://developers.facebook.com
- Create a new App → choose "Business" type
- Add these products to your app:
  - **Instagram Graph API**
  - **Instagram Basic Display**

### 4. Get Your Tokens

#### Step A — Get a short-lived User Access Token
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your App
3. Click "Generate Access Token"
4. Add these permissions:
   ```
   instagram_basic
   instagram_content_publish
   instagram_manage_insights
   pages_show_list
   pages_read_engagement
   ```
5. Click "Generate Token" and copy it

#### Step B — Exchange for a Long-Lived Token (60 days)
```bash
curl -X GET "https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=YOUR_APP_ID
  &client_secret=YOUR_APP_SECRET
  &fb_exchange_token=SHORT_LIVED_TOKEN"
```
Copy the `access_token` from the response → put in `.env` as `IG_ACCESS_TOKEN`

#### Step C — Get Your Instagram Business Account ID
```bash
curl "https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_LONG_TOKEN"
# Returns Facebook Page ID

curl "https://graph.facebook.com/v19.0/YOUR_PAGE_ID?fields=instagram_business_account&access_token=YOUR_TOKEN"
# Returns {"instagram_business_account": {"id": "YOUR_IG_ACCOUNT_ID"}}
```
Put this in `.env` as `IG_BUSINESS_ACCOUNT_ID`

#### Step D — Token Refresh (set a cron job for every 50 days)
```bash
# Add this to your crontab:
0 9 1 * * curl "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=CURRENT_TOKEN" > /tmp/new_token.json
```

---

## API Rate Limits & Constraints

| Limit | Value | Our mitigation |
|-------|-------|----------------|
| Posts per 24h | 50 API-created posts | We post max 2/day — safe |
| Stories per day | 25 | Not used in MVP |
| API calls per hour | 200 per token | Well within range |
| Reel video length | 3s – 90s | Script generates 60s reels |
| Image size | JPEG/PNG, 8MB max | DALL-E outputs are fine |
| Image ratio | 4:5 to 1.91:1 | We use 1:1 (square) |
| Carousel items | 2–10 | We cap at 8 |
| Caption length | 2,200 chars, 30 hashtags | Enforced in client |
| Hashtags per post | Max 30 | We use 25 |

---

## Risks & How to Avoid Bans

### ✅ Safe practices (what we do)
- Use the **official Graph API** — never Selenium/scraping
- Post at human-like intervals (min 4h between posts)
- Don't use bot-like captions (identical text on multiple posts)
- Vary hashtag sets across posts (40-50% overlap max)
- Respect daily post limits (we use 1-2/day max)

### ⚠ Risk factors to monitor
- **Token expiry**: Tokens expire in 60 days — set up refresh cron
- **Permission changes**: Meta changes permissions sometimes without notice
- **Insights delay**: Engagement data takes 30min–2h to appear
- **Video processing**: Reels can take 5-15 min to process

### ❌ What NOT to do
- Don't use `instaloader`, `selenium`, unofficial libraries
- Don't follow/unfollow in bulk
- Don't use the same caption for A and B variants (IG detects duplicates)
- Don't post more than 3x/day even with API

---

## Cloudinary Setup (free image hosting)

```bash
pip install cloudinary
```

1. Sign up at https://cloudinary.com (free: 25GB storage, 25 credits/month)
2. Go to Dashboard → copy Cloud Name, API Key, API Secret
3. Add to `.env`

That's it. The `creative_agent.py` handles the rest.

---

## Production checklist

- [ ] Long-lived token in `.env`
- [ ] Cloudinary credentials in `.env`
- [ ] OpenAI API key in `.env`
- [ ] SQLite DB initialized (`python main.py generate --dry-run`)
- [ ] Test post with `POST /posts/{id}/approve` flow
- [ ] Set up token refresh cron
- [ ] Monitor `/posts` endpoint for failed status
