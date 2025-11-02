# Create Job Application

Create a complete job application package for a specific job posting.

## Usage

```
/create-job-application <job_url>
```

## Arguments

- `job_url`: URL to the job posting (required)

## Description

This command automates the complete job application workflow:

1. **Job Analysis**: Extracts job details from the provided URL
2. **Company Research**: Gathers information about the company, culture, and mission  
3. **Folder Setup**: Creates `.job_applications/<company_name>/<job_slug>/` directory structure
4. **Documentation**: Generates `job_details.md` with role requirements and company info
5. **Resume Customization**: Creates tailored `resume-<job-slug>.json` based on static/resume.json
6. **PDF Generation**: Uses `make engineering-pdf` to create customized PDF CV
7. **User Interaction**: Presents analysis and gathers user input about role excitement
8. **Cover Letter**: Generates `cover_letter.md` based on user input and job fit analysis
9. **Cover Letter PDF**: Uses `npx md-to-pdf` to create professional PDF cover letter
10. **Application Guide**: Provides `application_notes.md` with form guidance and job URL reference
11. **Daily Worklog**: Records application details in `.job_applications/<yyyy-mm-dd>.worklog.md`

## Example

```
/create-job-application https://job-boards.greenhouse.io/dittoliveincorporated/jobs/4587786006
```

This will create:
```
.job_applications/ditto/staff-sre-emea/
├── job_details.md              # Job description, requirements, company info
├── resume-staff-sre-emea.json  # Customized resume for this role
├── resume-staff-sre-emea.pdf   # Generated PDF CV (engineering theme)
├── cover_letter.md             # Tailored cover letter
├── cover_letter.pdf            # Professional PDF cover letter (md-to-pdf)
└── application_notes.md        # Application form guidance and job URL

.job_applications/2025-08-09.worklog.md  # Daily activity log
```