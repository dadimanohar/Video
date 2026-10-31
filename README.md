# Daily AI Shorts Studio

A free-first scheduled AI-news Shorts pipeline for the YouTube channel. GitHub Actions is the execution host; this repository is the source and dashboard. It is not an always-on web server.

## Pipeline
1. Discover AI news from official OpenAI, Google, NVIDIA and Anthropic publisher feeds; links are restricted to those official domains.
2. Prioritise recent entries (up to 14 days), fetch readable article text where available, and reject weakly supported or stale stories.
3. Generate a validated Indian Professional English script using Gemini.
4. Narrate with offline eSpeak NG.
5. Render a vertical MP4 with compact captions using FFmpeg.
6. Upload through YouTube Data API OAuth.
7. Preserve the video, script, metadata and upload receipt as a 7-day Actions artifact.

## Schedule
Daily at 09:00 Asia/Kolkata (03:30 UTC). Manual workflow runs are also supported.

## Dashboard hosting
The dashboard source is `index.html`. Open Settings → Pages and select **GitHub Actions** as the build and deployment source. GitHub Pages is static hosting only; scheduled backend work runs in GitHub Actions.

## Configure secrets
Repository Settings → Secrets and variables → Actions:
- `GEMINI_API_KEY`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

Optional repository variable:
- `YOUTUBE_PRIVACY`: `private`, `unlisted` or `public`. Default is `private`.

Do not commit secrets or send them in chat. Create a Gemini API key in Google AI Studio. Enable YouTube Data API v3 in Google Cloud and create OAuth credentials. The refresh token must be authorized by the channel owner with the `youtube.upload` scope.

## Test
1. The **Pipeline Smoke Test** runs source/date regression tests, fetches a publisher feed item and creates a clearly labelled demo MP4 without Gemini or YouTube credentials.
2. Download and inspect the `daily-shorts-pipeline-demo` artifact.
3. After configuring all four secrets, run **Daily AI News Short** manually.
4. Verify the uploaded video's privacy and playback before relying on the daily schedule.

## Honest limitations
- This is a scheduled runner, not a persistent server process.
- Demo mode is not a news publication and does not upload.
- Production generation and upload require owner-configured API secrets.
- Gemini quotas and Google OAuth verification requirements can change.
- The offline voice is synthetic; visuals are a motion title card and captions, not cinematic AI footage.
- Uploads default to private. Change the repository variable only when the intended visibility has been explicitly selected.
