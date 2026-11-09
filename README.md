# CropConsult AI starter app

A local Streamlit crop scouting and report application. Stores reports in a local SQLite database, creates PDFs, includes an input cost calculator, and optionally drafts report language using the OpenAI API.

## Start
1. Install Python 3.10+.
2. In this folder run: `pip install -r requirements.txt`
3. Run: `streamlit run app.py`
4. Open the local address shown in the terminal.

Optional AI: Set environment variable `OPENAI_API_KEY` before launching. OpenAI API usage may incur charges. AI text is a draft and is not automatically saved to the database.

## Limitations
Single-computer prototype, no login or cloud sync, no automatic weather or field imagery, no photo uploads. Back up `cropconsult.db`. Do not expose this app publicly without authentication, encryption, access controls, and appropriate data handling safeguards. All agronomic recommendations require professional review and label compliance.
