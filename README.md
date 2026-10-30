# Daily AI Shorts Studio

A free-first scheduled AI-news Shorts pipeline for the YouTube channel. GitHub Actions is the execution host; this repository is the source and dashboard. It is not an always-on web server.

## Pipeline
1. Discover AI news from official publisher RSS feeds.
2. Generate a short Indian Professional English script using Gemini.
3. Narrate with offline eSpeak NG (no paid TTS).
4. Render a vertical MP4 with captions using FFmpeg.
5. Upload through YouTube Data API OAuth.
6. Preserve the video, script, metadata and upload receipt as a 7-day Actions artifact.

## Schedule
Daily at 09:00 Asia/Kolkata (03:30 UTC). Manual workflow runs are also supported.

## Configure secrets
Repository Settings → Secrets and variables → Actions:
- `GEMINI_API_KEY`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

Optional repository variable:
- `YOUTUBE_PRIVACY`: `private`, `unlisted` or `public`. Default is `private`.

Do not commit secrets or send them in chat. Use Google AI Studio for a Gemini API key and Google Cloud Console to enable YouTube Data API v3 and create OAuth credentials. The refresh token must be authorized by the channel owner with `youtube.upload` scope.

## Test
1. Run **Pipeline Smoke Test** first. This test fetches an official feed item and creates a clearly labelled demo MP4 without Gemini or YouTube credentials.
2. Download and inspect the `daily-shorts-pipeline-demo` artifact.
3. After configuring all secrets, run **Daily AI News Short** manually.
4. Verify the uploaded video's privacy and playback before relying on the daily schedule.

## Honest limitations
- This is a scheduled serverless-style pipeline, not a persistent server process.
- The demo mode is not a real news video and does not publish.
- Production generation and upload cannot succeed until the owner configures API secrets.
- Gemini quotas and Google OAuth verification requirements can change.
- The offline voice is synthetic; visuals are an animated title card and captions, not cinematic AI footage.
- Google may restrict unverified YouTube API projects to private uploads.
