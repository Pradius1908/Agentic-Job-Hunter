# Jobify — AI Job Search Assistant

Jobify is a Streamlit web app that helps users find jobs with the help of AI. It combines a resume parser, a saved preferences profile, and an AI-powered job search agent that turns plain-English requests into real job listings scraped from sites like LinkedIn, Indeed, Naukri, Glassdoor, and Google Jobs.

It's built to run inside Google Colab, with the Streamlit app tunneled to a public URL using `ngrok`.

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [How It Works (End-to-End Flow)](#how-it-works-end-to-end-flow)
4. [Page-by-Page Breakdown](#page-by-page-breakdown)
   - [Home Page](#home-page-homepy)
   - [Resume Analyser](#resume-analyser-pagesrespy)
   - [Your Preferences](#your-preferences-pagesprefpy)
   - [AI Job Search](#ai-job-search-pagesajpy)
5. [Database (SQLite)](#database-sqlite)
6. [AI Agent & Structured Output](#ai-agent--structured-output)
7. [Setup & Running the App](#setup--running-the-app)
8. [API Key Configuration](#api-key-configuration)
9. [Known Limitations](#known-limitations)

---

## Overview

Jobify is made up of three connected pages:

- **Resume Analyser** — upload a PDF resume and get key details (name, email, phone, skills) automatically extracted and displayed.
- **Your Preferences** — a form where the user sets up (or edits) their job search profile: desired role, location, industry, experience level, preferred job sites, and how recent job postings should be.
- **AI Job Search** — the main feature. Either uses the saved profile or a typed natural-language request to search live job listings via an AI agent, then displays the results as filterable, sortable job cards.

All saved profile data lives in a single local SQLite database (`jobify_user.db`), which ties the three pages together — information entered or extracted on one page is available on the others.

---

## Project Structure

```
.
├── home.py              # Landing page
├── pages/
│   ├── res.py            # Resume Analyser page
│   ├── pref.py           # Your Preferences page
│   └── aj.py             # AI Job Search page
├── jobify_user.db        # SQLite database (created automatically)
├── uimage.jpg            # Hero banner image (home page)
├── resume.png            # Icon for "Upload Resume" card
├── choicetr.png          # Icon for "Your Preferences" card
└── jobtr.png              # Icon for "AI Job Search" card
```

Streamlit automatically treats any `.py` file inside `pages/` as a separate page in the sidebar navigation, with `home.py` (or the main script) as the entry point.

---

## How It Works (End-to-End Flow)

A typical user journey looks like this:

1. **Land on the Home page** — see an overview of the app and three navigation cards.
2. **Upload a resume** on the Resume Analyser page — the app extracts the candidate's name, email, phone, and skills, and displays them in a dashboard.
3. **Save those details to a profile** — stored in the SQLite database.
4. **Go to Your Preferences** — fill in or adjust the desired job title, location, industry, experience level, preferred job sites, and posting recency window. Save the profile.
5. **Go to AI Job Search**:
   - If a profile exists, the app shows a "Profile Detected" banner and offers a one-click "Search Using My Profile" button.
   - Alternatively, the user can type a free-form request like *"I want Python developer jobs in Bengaluru from LinkedIn and Naukri posted in the last 3 days."*
6. **The AI agent (Gemini)** reads the request and converts it into structured search parameters (job title, location, sites, recency, remote/job type, etc.).
7. **The app scrapes live job listings** from the selected sites based on those parameters.
8. **Results are displayed** as styled job cards — title, company, location, salary, posting date, description, and "Apply" links — with sidebar filters (site, job type, remote-only, minimum salary) and sorting options, plus a CSV export.

---

## Page-by-Page Breakdown

### Home Page (`home.py`)

The landing page sets up the overall visual identity of the app:

- A large hero banner image with a faded/masked effect and overlaid title text ("JOBIFY — Your AI Job-Search Assistant").
- An introductory paragraph describing what the app does.
- Three clickable cards, each linking to one of the other pages:
  - **Upload Resume** → Resume Analyser
  - **Your Preferences** → Preferences form
  - **AI Job Search** → AI-powered job search

Each card has a hover animation (lift + glow effect) for a polished feel.

### Resume Analyser (`pages/res.py`)

This page lets the user upload a resume as a PDF and get an instant analysis:

1. **Text extraction** — the PDF's text content is extracted in full.
2. **Cleanup** — extra whitespace is collapsed, and known resume section headings (SKILLS, EDUCATION, WORK EXPERIENCE, PROJECTS, etc.) are used to re-introduce line breaks, making the text easier to parse.
3. **Information extraction** — using pattern matching (not AI), the app pulls out:
   - **Name** — assumed to be the first capitalized word(s) near the top of the document.
   - **Email** and **Phone Number** — matched via standard formats.
   - **Skills** — found by locating the SKILLS section and splitting it into individual skill tags, cleaning up labels and bullet characters.
   - **Education** and **Work Experience** — extracted as text blocks (computed but not currently shown on the dashboard).
4. **Dashboard display** — the extracted name appears in a profile banner, email and phone are shown in side-by-side cards, skills appear as colored "pill" tags, and the full cleaned resume text is available in an expandable section.
5. **Save to Profile** — a button saves the extracted name, email, phone, and skills into the SQLite database, and links the user to the Preferences page to fill in the rest.

> Note: This is **not** an AI-generated summary — it's deterministic text-pattern extraction. It works best on resumes that use standard section headings.

### Your Preferences (`pages/pref.py`)

This page is a settings form for the user's job search profile, pre-filled with any previously saved data:

- **Personal info**: full name, email, phone (carried over from the resume if saved).
- **Job search criteria**:
  - Desired job title (required)
  - Preferred location
  - Preferred industry
  - Experience level (Entry, Mid, Senior, Lead/Manager, Executive)
  - Preferred job sites (LinkedIn, Indeed, Glassdoor, Naukri, Google)
  - How recent job postings should be (24–720 hours)
  - Key skills (comma-separated)

Buttons let the user:
- **Save Preferences** — validates that name and job title are filled in, then writes the profile to the database (replacing any previous profile — only one profile is stored at a time).
- **Clear Saved Data** — wipes the saved profile.
- **Save details from Resume instead** — jumps back to the Resume Analyser.

A preview of the currently saved profile is shown below the form once data exists.

### AI Job Search (`pages/aj.py`)

The core feature of the app. It offers two ways to search:

**1. Profile-based search**
If a saved profile with a desired job title exists, a banner displays the detected profile (name, role, location, sites). Clicking "Search Using My Profile" automatically builds a natural-language search sentence from the saved preferences (e.g. *"I want Data Analyst jobs in Bengaluru, India from linkedin, naukri posted in the last 72 hours"*) and runs it through the AI search pipeline below.

**2. Manual search**
The user types their own request in plain English into a search box, optionally adjusting advanced settings (results per site, max posting age).

**The AI search pipeline (for both paths):**

1. The request text is sent to an AI agent powered by Google's **Gemini 2.5 Flash** model.
2. The agent reads the sentence and converts it into structured search settings: job title, location, which job sites to search, how many results, how recent, country, whether remote is requested, and job type (full-time, part-time, internship, contract).
3. Job site names are normalized (so variations like "LinkedIn.com" or "Google Jobs" are mapped correctly), and any sites mentioned in the request that aren't supported by the scraping library are flagged separately so the user knows they were skipped.
4. The app scrapes live job listings from the resolved sites and parameters.
5. Results are stored for the session so filters can be applied without re-searching.

**Displaying results:**

- Each job is shown as a card with title, company, location, source site, posting date, salary (when available), badges for job type/remote/experience level, a short description (expandable for the full text), extra details (skills required, openings, contact info if available), and a company info box (industry, size, revenue, HQ, company page link) when the data is available.
- "Apply Now" and "Apply on Company Site" buttons link directly to the listing.
- A sidebar lets the user filter by source site, job type, remote-only, and minimum salary, and sort by recency, salary, or company name.
- All results can be downloaded as a CSV file.
- If a site (commonly Naukri) returns zero results, a diagnostic message explains this is usually a scraper-side issue (rate limiting, blocking) rather than the search terms.

---

## Database (SQLite)

A single SQLite database file, **`jobify_user.db`**, stores one table:

| Column | Description |
|---|---|
| `id` | Primary key |
| `full_name` | User's name |
| `email` | User's email |
| `phone` | User's phone number |
| `desired_job_title` | Target job role |
| `preferred_location` | Target location |
| `preferred_sites` | Comma-separated list of job sites to search |
| `experience_level` | Entry / Mid / Senior / Lead-Manager / Executive |
| `skills` | Comma-separated skills |
| `preferred_industry` | Target industry |
| `hours_old` | Max age (in hours) of job postings to show |

- The **Resume Analyser** page can insert or update `full_name`, `email`, `phone`, and `skills`.
- The **Preferences** page manages the full record — saving replaces the existing row (so there's always at most one profile), and it can also clear the table entirely.
- The **AI Job Search** page reads the latest profile (if any) to power the profile-based search, and gracefully handles a missing or empty database.

---

## AI Agent & Structured Output

The job search feature uses **LangChain** with a **Gemini 2.5 Flash** model configured to return a structured response matching a predefined schema. Instead of returning free text, the model fills in fields such as:

- `site` — which job sites to search
- `search_term` — the job title/role
- `google_search_term` — a natural-language query for Google Jobs
- `location`
- `results_wanted` — number of results per site
- `hours_old` — max age of postings
- `country_indeed` — country for Indeed/Glassdoor
- `is_remote` — whether remote work was requested
- `job_type` — full-time, part-time, internship, or contract

This structured data is then passed to the job-scraping library, which queries the actual job sites and returns real listings as a table, which the app turns into the visual job cards.

If the AI call fails for any reason (network issue, rate limit, etc.), the app falls back to sensible default search settings rather than crashing.

---

## Setup & Running the App

This project is designed to run in **Google Colab**:

1. Install dependencies:
   ```
   pip install streamlit pyngrok python-jobspy langchain langchain-google-genai pdfminer.six -q
   ```
2. Write out the page files (`home.py`, `pages/res.py`, `pages/pref.py`, `pages/aj.py`) using `%%writefile` cells.
3. Set up your API keys (see below).
4. Launch Streamlit and tunnel it with ngrok:
   ```python
   from pyngrok import ngrok
   import subprocess

   process = subprocess.Popen(["streamlit", "run", "home.py"])
   public_url = ngrok.connect(8501)
   print(public_url)
   ```
5. Open the printed public URL to use the app.

To stop the tunnel, use `ngrok.kill()` or disconnect active tunnels via `ngrok.get_tunnels()`.

---

## API Key Configuration

The app needs two secrets:

- **NGROK auth token** — used to create the public tunnel.
- **Gemini API key** — used by the AI search agent.

Both should be stored securely rather than hardcoded:

- In Colab, store them in the **Secrets** panel (key icon in the sidebar) and load them with `userdata.get(...)`.
- Set them as environment variables before launching Streamlit (e.g. `os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI")`), then read them inside the page scripts with `os.environ.get("GEMINI_API_KEY")`. This works because the Streamlit subprocess inherits the notebook's environment at launch time.
- Alternatively, use Streamlit's `secrets.toml` file (`st.secrets["GEMINI_API_KEY"]`), keeping it out of version control.



---

## Known Limitations

- Resume parsing is regex/pattern-based, not AI-based — it works best with resumes that use standard section headings (SKILLS, EDUCATION, WORK EXPERIENCE, etc.).
- Only one user profile can be saved at a time (saving a new profile replaces the old one).
- Job scraping depends on third-party sites' structure and rate limits — some sites (notably Naukri) may intermittently return zero results due to scraper-side blocking, not search settings.
- Some job sites commonly requested by users (e.g. Monster, Internshala) are not supported by the underlying scraping library and will be flagged as unsupported if mentioned.
- The app currently supports only one saved profile and one resume upload session at a time — there's no multi-user account system.
