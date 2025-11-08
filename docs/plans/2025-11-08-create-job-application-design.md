# `/create-job-application` Command Design

**Date:** 2025-11-08
**Status:** Design
**Context:** Extract job application tooling from `scratchpad/davidlaing.com-with-jobapplication-wip/` and integrate into WCTF framework

## Overview

A slash command in WCTF that generates tailored application materials using existing company research, stores them in the WCTF data structure, and publishes PDFs to davidlaing.com with obscured URLs for privacy.

## Goals

1. **Leverage WCTF research** - Use facts, flags, and insider intel to create informed applications
2. **Test WCTF predictions** - Track applications through pipeline to validate framework accuracy
3. **Professional output** - Generate high-quality CVs and cover letters with proper branding
4. **Privacy** - Obscure PDF URLs while keeping downloaded filenames professional
5. **Simplicity** - No complex skills, just slash commands with good prompts

## Command Signature

```bash
/create-job-application <job_url>
```

**Example:**
```bash
/create-job-application https://jobs.apple.com/en-ie/details/200566030-0562/site-reliability-engineer
```

## Workflow

### 1. Extract Job Details

Parse the job posting URL to extract:
- Company name
- Job title
- Team name (if available)
- Role number/ID
- Requirements and qualifications
- Job description

Save to: `data/stage-2/<company>/applications/<job-slug>/job-details.md`

### 2. Read Source Data

**WCTF research (if available):**
- `data/stage-2/<company>/company.facts.yaml` - Company research
- `data/stage-2/<company>/company.flags.yaml` - Evaluation flags
- `data/stage-2/<company>/company.insider.yaml` - Insider intelligence

**Resume data:**
- `/workspace/active/projects/davidlaing-com/static/resume.json` - Experience and background

### 3. Generate Application Materials (Markdown)

**CV (`mrdavidlaing-cv-YYYYMMDD.md`):**
- Tailored to job requirements
- Highlights relevant experience from resume.json
- Emphasizes: scale achievements, matching tech stack, relevant skills
- Format: Professional markdown suitable for PDF conversion

**Cover Letter (`mrdavidlaing-cover-letter-YYYYMMDD.md`):**
- Uses **WCTF-informed but subtle approach** (Approach C):
  - Demonstrates deep research and understanding
  - Shows knowledge of tech stack, scale challenges, team focus
  - Uses insider intel strategically (practices, tools, culture)
  - Avoids revealing red flags (silos, satellite status, career ceiling)
- Tone: Enthusiastic about technical challenges, evidence-based, forward-looking
- Length: 1-2 pages

Save to: `data/stage-2/<company>/applications/<job-slug>/`

### 4. Generate Short-SHA and Track Application

**Generate random 5-character identifier:**
- Format: `[a-z0-9]{5}` (e.g., "a7f3k")
- Purpose: Obscure PDF URLs for privacy
- Links markdown sources → PDF URLs in tracking

**Create/update application tracking:**

File: `data/stage-2/<company>/company.applications.yaml`

```yaml
applications:
  - short_sha: "a7f3k"
    job_url: "https://jobs.apple.com/en-ie/details/200566030-0562/..."
    job_title: "Site Reliability Engineer"
    team: "Cloud Services SRE"
    role_number: "200566030-0562"
    applied_date: "2025-11-08"
    status: "applied"

    # WCTF context
    wctf_verdict: "DECLINE"  # or "ACCEPT", "MAYBE"
    wctf_reason: "35% burnout work, severe organizational coherence violations"
    test_rationale: "Using as test case to validate WCTF process"

    # Generated materials
    materials:
      cv_markdown: "applications/sre-cloud-services/mrdavidlaing-cv-20251108.md"
      cover_letter_markdown: "applications/sre-cloud-services/mrdavidlaing-cover-letter-20251108.md"
      cv_pdf_url: "https://davidlaing.com/wctf/a7f3k/mrdavidlaing-cv-20251108.pdf"
      cover_letter_pdf_url: "https://davidlaing.com/wctf/a7f3k/mrdavidlaing-cover-letter-20251108.pdf"

    # Insider contact (if available)
    insider_contact:
      name: "James Wynne"
      role: "Staff Engineer, Cloud OS SRE"
      relationship: "Conducted insider interview 2025-10-22"
      referral_status: "available_if_needed"  # Note for later, not auto-requested

    # Predictions to validate during interviews
    predictions_to_validate:
      - "LeetCode-focused interview despite Staff-level role"
      - "Satellite office dynamics mentioned by interviewers"
      - "Silos evident in team structure discussion"
      - "Career ceiling at Staff/Team Lead in Dublin"
      - "DORA metrics and AI tooling confirmed"

    # Application timeline
    timeline:
      applied: "2025-11-08"
      # Future: phone_screen, technical_interview, onsite, offer, decision
```

### 5. Convert Markdown to PDF

**Tool:** `npx md-to-pdf`

**Styling:** davidlaing-com solarized-light CSS (consistent with site branding)

**Output naming:**
- `mrdavidlaing-cv-20251108.pdf`
- `mrdavidlaing-cover-letter-20251108.pdf`

**Process:**
1. Generate PDFs from markdown
2. Verify PDFs created successfully
3. Move to final destination

### 6. Publish PDFs to davidlaing.com

**Destination:** `/workspace/active/projects/davidlaing-com/static/wctf/<short-sha>/`

**Structure:**
```
davidlaing-com/static/wctf/
└── a7f3k/                                    # Obscured folder
    ├── mrdavidlaing-cv-20251108.pdf          # Professional filename
    └── mrdavidlaing-cover-letter-20251108.pdf
```

**Resulting URLs:**
- `https://davidlaing.com/wctf/a7f3k/mrdavidlaing-cv-20251108.pdf`
- `https://davidlaing.com/wctf/a7f3k/mrdavidlaing-cover-letter-20251108.pdf`

**Benefits:**
- URLs are obscured (not guessable)
- Downloaded files have professional names
- Short-sha links back to application tracking

### 7. Output Application Summary

Display to user:
- ✅ Generated CV and cover letter
- ✅ Created PDFs with branding
- ✅ Published to davidlaing.com
- 📋 Application URLs (ready to paste)
- 🔍 WCTF predictions to validate
- 📝 Next steps / application guidance

## Directory Structure

### WCTF Repository

```
/workspace/active/projects/wctf/
├── .claude/
│   └── commands/
│       └── create-job-application.md    # NEW: Slash command
├── docs/
│   └── plans/
│       └── 2025-11-08-create-job-application-design.md  # This document
└── data/
    └── stage-2/
        └── <company>/
            ├── company.facts.yaml
            ├── company.flags.yaml
            ├── company.insider.yaml
            ├── company.applications.yaml    # NEW: Application tracking
            └── applications/                # NEW: Per-job materials
                └── <job-slug>/
                    ├── job-details.md
                    ├── mrdavidlaing-cv-YYYYMMDD.md
                    └── mrdavidlaing-cover-letter-YYYYMMDD.md
```

### davidlaing-com Repository

```
/workspace/active/projects/davidlaing-com/
├── static/
│   ├── resume.json                      # Source of truth for experience
│   └── wctf/                            # NEW: Application PDFs
│       └── <short-sha>/                 # Obscured folder per application
│           ├── mrdavidlaing-cv-YYYYMMDD.pdf
│           └── mrdavidlaing-cover-letter-YYYYMMDD.pdf
└── styles/
    └── solarized-light.css              # Branding for PDFs
```

## Dependencies

### External Tools
- **npx md-to-pdf** - Markdown to PDF conversion (Node.js)
- **Solarized-light CSS** - davidlaing-com branding stylesheet

### Data Sources
- **resume.json** - `/workspace/active/projects/davidlaing-com/static/resume.json`
- **WCTF research** - `data/stage-2/<company>/company.{facts,flags,insider}.yaml`

### Removed Dependencies
- ~~Generic `markdown-to-pdf` skill~~ - Use `npx md-to-pdf` directly
- ~~Generic `resume-builder` skill~~ - Claude generates markdown directly
- ~~JSON Resume conversion~~ - Not needed, Claude reads resume.json and writes markdown

## Cover Letter Strategy

### Approach: WCTF-Informed but Subtle (Approach C)

**Demonstrate knowledge through:**
- Specific technology mentions (matching job requirements)
- Understanding of scale challenges (from facts)
- SRE principles and practices (from job description)
- Team-specific details (from insider intel, used carefully)
- Relevant experience alignment (from resume.json)

**Avoid revealing:**
- Negative flags (silos, satellite status, career ceiling)
- Specific insider interview quotes or details
- WCTF verdict reasoning
- Internal concerns about organizational structure

**Tone:**
- Enthusiastic about technical challenges
- Evidence-based (cite specific achievements)
- Forward-looking (what you'd contribute)
- Professional and genuine

**Example knowledge to incorporate for Apple SRE:**
- "Supporting services at exabyte scale across hundreds of millions of users"
- "Kubernetes ecosystem, Cassandra, Kafka, Redis infrastructure"
- "SRE principles including error budgets, toil elimination, fault analysis"
- "Cloud Services Infrastructure team building next-generation platform"

## Referral Handling

**Approach: Note for later (Approach B)**

When insider contact exists:
1. Document in `insider_contact` section of application tracking
2. Set `referral_status: "available_if_needed"`
3. Leave timing and approach to user (relationship-dependent)
4. DO NOT auto-generate referral requests or reach out

**Rationale:** Referrals are relationship-sensitive and timing-dependent. User should control when/how to engage insider contacts.

## Testing Strategy

### Test Case: Apple SRE Role

**Job:** https://jobs.apple.com/en-ie/details/200566030-0562/site-reliability-engineer

**WCTF Research:** Complete (stage-2)
- Facts: ✅ Company research done
- Flags: ✅ Energy Matrix shows DECLINE verdict
- Insider: ✅ James Wynne interview 2025-10-22

**Expected Output:**
1. Professional CV highlighting: SRE experience, scale, K8s, Python/Go/Rust
2. Cover letter demonstrating: Understanding of Cloud Services team, infrastructure scale, SRE practices
3. PDFs published to: `https://davidlaing.com/wctf/<short-sha>/mrdavidlaing-*-20251108.pdf`
4. Application tracking with: WCTF predictions, insider contact, timeline tracking

**Validation Points:**
- CV accurately reflects resume.json experience
- Cover letter uses WCTF intel without revealing red flags
- PDFs render correctly with solarized-light branding
- URLs are obscured but filenames are professional
- Application tracking captures all metadata
- Predictions align with WCTF Energy Matrix analysis

## Implementation Plan

### Phase 1: Slash Command Creation
1. Create `.claude/commands/create-job-application.md`
2. Write comprehensive prompt with all workflow steps
3. Test with Apple SRE role

### Phase 2: Application Tracking Schema
1. Define `company.applications.yaml` structure
2. Create template with all required fields
3. Test tracking with Apple application

### Phase 3: PDF Generation
1. Locate/create solarized-light CSS in davidlaing-com
2. Test `npx md-to-pdf` with custom styling
3. Verify PDF quality and branding

### Phase 4: Integration Testing
1. Run full workflow for Apple SRE role
2. Verify all files created in correct locations
3. Test PDF URLs are accessible
4. Validate application tracking completeness

### Phase 5: Documentation
1. Update WCTF README with application workflow
2. Document slash command usage
3. Create example application (anonymized)

## Migration from Existing Tooling

### Source: `scratchpad/davidlaing.com-with-jobapplication-wip/`

**What to preserve:**
- `static/resume.json` - Keep in davidlaing-com as source of truth
- Solarized-light CSS - Copy to davidlaing-com styles
- Example applications - Use as reference for quality

**What to migrate:**
- Slash command concept → WCTF `.claude/commands/`
- Application tracking approach → `company.applications.yaml`
- PDF output → `davidlaing-com/static/wctf/`

**What to remove:**
- Generic skills (`markdown-to-pdf`, `resume-builder`)
- Hugo-specific tooling (not needed for PDFs)
- Separate `.job_applications/` directory structure

## Success Criteria

1. **Workflow works end-to-end** - Single command generates complete application package
2. **PDFs are professional** - Branding matches davidlaing.com, downloads have good names
3. **URLs are private** - Short-sha obscures links, not guessable
4. **WCTF integration** - Uses existing research, tracks predictions
5. **Simplicity** - No complex skills, just prompts and standard tools
6. **Testable** - Can validate predictions as application progresses

## Future Enhancements (Not in Scope)

- On-demand PDF generation via Cloudflare Pages functions
- Automated application status tracking (requires external integrations)
- Multi-company application campaigns
- A/B testing different cover letter approaches
- Analytics on application success rates

## Notes

- **Pre-build PDFs** chosen over on-demand conversion for control and simplicity
- **Short-sha** provides privacy without complex auth
- **Markdown sources** preserved in WCTF for version control and auditing
- **Professional filenames** ensure good download experience for recruiters
- **WCTF integration** enables testing framework predictions in real world
