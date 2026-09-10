# PersonaForge AI — Render Ready

A Render-ready Gradio prototype for PersonaForge AI: character creation, roleplay, voice profiles, memories, script generation, script analysis, and projects.

## Deploy on Render

- **Runtime:** Python
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `python app.py`
- **Port:** automatically uses Render's `PORT` environment variable.
- **Environment variable:** `GEMINI_API_KEY` (optional; required for Gemini-powered generation).

Never commit API keys to GitHub.

## Important

This prototype stores local app data in `personaforge_data.json`. Render's free web service has ephemeral storage, so local data can be lost on redeploy/restart. For production persistence, connect a database such as Supabase/Postgres.

Actual voice cloning requires an authorized third-party voice provider/API. The app only stores voice profiles and checks authorization for uploaded/cloned voices.
