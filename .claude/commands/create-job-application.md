# Create Job Application

Generate a complete job application package using WCTF research and resume data.

## Usage

```
/create-job-application <job_url>
```

Or with job posting text directly in conversation context:

```
/create-job-application
[Job posting text should already be in the conversation]
```

## Arguments

- `job_url`: URL to the job posting (optional if job text already in conversation)

## Description

This command creates a tailored job application using existing WCTF research (facts, flags, insider intel) combined with your resume data. It generates professional markdown documents, converts them to branded PDFs, and publishes them to davidlaing.com with obscured URLs.

You can provide either:
1. A URL to fetch the job posting, OR
2. The job posting text directly in the conversation (paste it before running the command)

## Workflow

You will execute the following steps:

### 1. Extract Job Details

**If job_url provided:** Fetch and parse the job posting from the URL.

**If no URL provided:** Use the job posting text from the conversation context (user should have pasted it in the previous message).

Extract:
- Company name
- Job title
- Team name (if mentioned)
- Role number/ID (if available)
- Key requirements and qualifications
- Job description and responsibilities

Create a markdown summary and save to:
`data/stage-2/<company>/applications/<job-slug>/job-details.md`

Where `<job-slug>` is a URL-friendly version of the job title (e.g., "site-reliability-engineer" or "sre-cloud-services").

### 2. Read Source Data

**WCTF Research (if available):**
- `data/stage-2/<company>/company.facts.yaml` - Company research
- `data/stage-2/<company>/company.flags.yaml` - Evaluation with Energy Matrix
- `data/stage-2/<company>/company.insider.yaml` - Insider intelligence

**Resume Data:**
- `/workspace/active/projects/davidlaing-com/static/resume.json` - David's experience and background

If WCTF research doesn't exist for this company, note that and proceed with resume data only.

### 3. Generate CV (Markdown)

Create a tailored CV in markdown format highlighting relevant experience from resume.json.

**Filename:** `mrdavidlaing-cv-YYYYMMDD.md` (use today's date)

**Content Strategy:**
- Start with a strong summary matching the role
- Highlight relevant technical skills and tools mentioned in job posting
- Emphasize scale achievements (PB-scale data, millions of users, etc.)
- Include relevant experience from resume.json
- Match language and terminology from job description
- Keep to 1-2 pages when rendered as PDF

**Format:**
- Clean professional markdown
- Use headers for sections (Summary, Experience, Skills, Education)
- Bullet points for achievements
- No complex formatting (tables, images, etc.)

Save to: `data/stage-2/<company>/applications/<job-slug>/mrdavidlaing-cv-YYYYMMDD.md`

### 4. Generate Cover Letter (Markdown)

Create a tailored cover letter using the **WCTF-informed but subtle approach**.

**Filename:** `mrdavidlaing-cover-letter-YYYYMMDD.md` (use today's date)

**Content Strategy:**

**DO demonstrate knowledge through:**
- Specific technologies from the job posting
- Understanding of scale challenges (from facts/job description)
- Relevant principles and practices (SRE, DevOps, etc.)
- Team-specific details (carefully, from insider intel if available)
- Alignment between your experience and their needs

**DO NOT reveal:**
- Negative WCTF flags (silos, organizational issues, etc.)
- Specific insider interview details or quotes
- WCTF verdict or reasoning
- Any concerns about the company/role

**Example for Apple SRE:**
- ✅ "Supporting services at exabyte scale across hundreds of millions of users"
- ✅ "Kubernetes ecosystem, Cassandra, Kafka infrastructure"
- ✅ "SRE principles including error budgets, toil elimination"
- ❌ "I understand there are challenges with satellite office dynamics"
- ❌ "I spoke with someone on the team who mentioned..."

**Tone:**
- Enthusiastic about technical challenges
- Evidence-based (cite specific achievements)
- Forward-looking (what you'd contribute)
- Professional and genuine
- 1-2 pages maximum

Save to: `data/stage-2/<company>/applications/<job-slug>/mrdavidlaing-cover-letter-YYYYMMDD.md`

### 5. Generate Short-SHA and Track Application

Generate a random 5-character identifier using lowercase letters and numbers (e.g., "a7f3k", "x9m2p").

Create or update `data/stage-2/<company>/company.applications.yaml` with the following structure:

```yaml
applications:
  - short_sha: "a7f3k"  # Random 5-char generated above
    job_url: "<full job posting URL>"
    job_title: "<job title from posting>"
    team: "<team name if mentioned>"
    role_number: "<role ID if available>"
    applied_date: "YYYY-MM-DD"  # Today
    status: "applied"

    # WCTF context (if research exists)
    wctf_verdict: "DECLINE|ACCEPT|MAYBE"  # From company.flags.yaml synthesis
    wctf_reason: "<brief summary from Energy Matrix analysis>"
    test_rationale: "<why applying despite verdict, if applicable>"

    # Generated materials
    materials:
      cv_markdown: "applications/<job-slug>/mrdavidlaing-cv-YYYYMMDD.md"
      cover_letter_markdown: "applications/<job-slug>/mrdavidlaing-cover-letter-YYYYMMDD.md"
      cv_pdf_url: "https://davidlaing.com/wctf/<short-sha>/mrdavidlaing-cv-YYYYMMDD.pdf"
      cover_letter_pdf_url: "https://davidlaing.com/wctf/<short-sha>/mrdavidlaing-cover-letter-YYYYMMDD.pdf"

    # Insider contact (if available from company.insider.yaml)
    insider_contact:
      name: "<name>"
      role: "<role>"
      relationship: "<how you know them>"
      referral_status: "available_if_needed"  # Note only, don't auto-request

    # Predictions to validate (from company.flags.yaml if available)
    predictions_to_validate:
      - "<specific prediction from WCTF research>"
      - "<another prediction to test in interviews>"

    # Timeline (will expand as application progresses)
    timeline:
      applied: "YYYY-MM-DD"
      # Future: phone_screen, technical_interview, onsite, offer, decision
```

**Notes:**
- If this is the first application for this company, create the file
- If company.applications.yaml already exists, append to the applications array
- Include WCTF context only if research exists
- Include insider contact only if company.insider.yaml exists
- Include predictions only if company.flags.yaml exists

### 6. Convert Markdown to PDF

Use `npx md-to-pdf` to convert both markdown files to PDFs with davidlaing-com branding.

**For CV:**
```bash
npx md-to-pdf data/stage-2/<company>/applications/<job-slug>/mrdavidlaing-cv-YYYYMMDD.md \
  --stylesheet /workspace/active/projects/davidlaing-com/styles/solarized-light.css \
  --pdf-options '{"format": "Letter", "margin": "20mm"}'
```

**For Cover Letter:**
```bash
npx md-to-pdf data/stage-2/<company>/applications/<job-slug>/mrdavidlaing-cover-letter-YYYYMMDD.md \
  --stylesheet /workspace/active/projects/davidlaing-com/styles/solarized-light.css \
  --pdf-options '{"format": "Letter", "margin": "20mm"}'
```

This will create PDFs in the same directory as the markdown files.

**Note:** If the solarized-light.css stylesheet doesn't exist yet, use the professional.css from the markdown-to-pdf skill as a fallback, or generate without a custom stylesheet.

### 7. Publish PDFs to davidlaing.com

Create the destination directory and copy PDFs:

```bash
mkdir -p /workspace/active/projects/davidlaing-com/static/wctf/<short-sha>

cp data/stage-2/<company>/applications/<job-slug>/mrdavidlaing-cv-YYYYMMDD.pdf \
   /workspace/active/projects/davidlaing-com/static/wctf/<short-sha>/

cp data/stage-2/<company>/applications/<job-slug>/mrdavidlaing-cover-letter-YYYYMMDD.pdf \
   /workspace/active/projects/davidlaing-com/static/wctf/<short-sha>/
```

**Result:** PDFs are now accessible at:
- `https://davidlaing.com/wctf/<short-sha>/mrdavidlaing-cv-YYYYMMDD.pdf`
- `https://davidlaing.com/wctf/<short-sha>/mrdavidlaing-cover-letter-YYYYMMDD.pdf`

**Benefits:**
- URLs are obscured (short-sha not guessable)
- Downloaded files have professional names
- Short-sha links back to application tracking in WCTF

### 8. Output Application Summary

Present the user with a summary of what was created:

```
✅ Application Package Created for <Company> - <Job Title>

📄 Generated Materials:
   CV:           data/stage-2/<company>/applications/<job-slug>/mrdavidlaing-cv-YYYYMMDD.md
   Cover Letter: data/stage-2/<company>/applications/<job-slug>/mrdavidlaing-cover-letter-YYYYMMDD.md

📊 Application Tracking:
   File: data/stage-2/<company>/company.applications.yaml
   Short-SHA: <short-sha>
   Status: applied

🌐 PDF URLs (paste in application form):
   CV:           https://davidlaing.com/wctf/<short-sha>/mrdavidlaing-cv-YYYYMMDD.pdf
   Cover Letter: https://davidlaing.com/wctf/<short-sha>/mrdavidlaing-cover-letter-YYYYMMDD.pdf

🔍 WCTF Predictions to Validate (if available):
   - <prediction 1>
   - <prediction 2>

📝 Next Steps:
   1. Review the generated CV and cover letter
   2. Copy the PDF URLs above
   3. Visit the job posting and submit your application
   4. Paste the CV and cover letter URLs into the application form
   5. Update application status in company.applications.yaml as it progresses
```

If WCTF research exists and shows a DECLINE verdict, also note:
```
⚠️  WCTF Verdict: DECLINE
    Reason: <brief reason from Energy Matrix>

    Note: Applying anyway to test WCTF process and validate predictions.
```

## Example

```bash
/create-job-application https://jobs.apple.com/en-ie/details/200566030-0562/site-reliability-engineer
```

**Expected output:**
- CV and cover letter tailored to Apple SRE role
- WCTF research used (facts, flags, James Wynne insider intel)
- PDFs published to obscured URL (e.g., davidlaing.com/wctf/a7f3k/)
- Application tracked with WCTF verdict (DECLINE) and predictions
- Professional materials ready to submit

## Error Handling

**If job URL cannot be fetched:**
- Ask user to provide job details manually (title, company, description)
- Continue with workflow using provided information

**If WCTF research doesn't exist:**
- Note that and proceed using only resume.json
- Generate professional materials without WCTF insights
- Suggest running WCTF research workflow first for better results

**If PDF conversion fails:**
- Check that npx and md-to-pdf are available
- Provide markdown files and ask user to convert manually
- Continue with tracking and URL generation (user can upload PDFs later)

**If davidlaing-com repo not found:**
- Save PDFs to temp directory
- Ask user to manually copy to davidlaing-com/static/wctf/<short-sha>/
- Provide full instructions for manual publication

## Related Documentation

- Design document: `docs/plans/2025-11-08-create-job-application-design.md`
- WCTF Framework: `WCTF_FRAMEWORK.md`
- Energy Matrix: `docs/plans/2025-01-08-energy-matrix-integration-design.md`

## Notes

- **Pre-build approach:** PDFs are generated immediately, not on-demand
- **Privacy via obscurity:** Short-SHA provides privacy without complex auth
- **Professional downloads:** Filenames are clean when recruiters download
- **WCTF integration:** Leverages existing research to inform applications
- **Prediction tracking:** Enables validation of WCTF framework accuracy
