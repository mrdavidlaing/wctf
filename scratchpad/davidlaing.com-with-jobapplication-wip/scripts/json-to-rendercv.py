#!/usr/bin/env python3
"""
Convert JSON Resume format to RenderCV YAML format with proper validation.
Uses the canonical resume.json as the single source of truth.
"""
import json
import yaml
import sys
import os

def convert_json_to_rendercv_yaml(json_file, output_file):
    """Convert JSON Resume to RenderCV YAML format."""
    
    # Read the JSON Resume
    with open(json_file, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    
    # Extract data from JSON Resume format
    basics = resume_data.get('basics', {})
    work = resume_data.get('work', [])
    education = resume_data.get('education', [])
    publications = resume_data.get('publications', [])
    projects = resume_data.get('projects', [])
    skills = resume_data.get('skills', [])
    
    # Build RenderCV structure
    rendercv_data = {
        'cv': {
            'name': basics.get('name', ''),
            'location': f"{basics.get('location', {}).get('city', '')}, {basics.get('location', {}).get('countryCode', '')}".strip(', '),
            'email': basics.get('email', ''),
            'social_networks': [],
            'sections': {}
        },
        'design': {
            'theme': 'engineeringresumes'
        }
    }
    
    # Convert social profiles to social_networks with required network field
    for profile in basics.get('profiles', []):
        rendercv_data['cv']['social_networks'].append({
            'network': profile.get('network', ''),
            'username': profile.get('username', '')
        })
    
    # Add summary section
    if basics.get('summary'):
        rendercv_data['cv']['sections']['summary'] = [basics['summary']]
    
    # Convert education
    if education:
        rendercv_data['cv']['sections']['education'] = []
        for edu in education:
            edu_entry = {
                'institution': edu.get('institution', ''),
                'area': edu.get('area', ''),
                'degree': edu.get('studyType', ''),
                'start_date': edu.get('startDate', ''),
                'end_date': edu.get('endDate', ''),
                'highlights': edu.get('courses', [])
            }
            rendercv_data['cv']['sections']['education'].append(edu_entry)
    
    # Convert work experience
    if work:
        rendercv_data['cv']['sections']['experience'] = []
        for job in work:
            job_entry = {
                'company': job.get('company', '') or job.get('name', ''),
                'position': job.get('position', ''),
                'start_date': job.get('startDate', ''),
                'highlights': job.get('highlights', [])
            }
            
            # Add optional fields
            if job.get('endDate'):
                job_entry['end_date'] = job['endDate']
            if job.get('location'):
                job_entry['location'] = job['location']
                
            rendercv_data['cv']['sections']['experience'].append(job_entry)
    
    # Convert publications with required authors field
    if publications:
        rendercv_data['cv']['sections']['publications'] = []
        for pub in publications:
            pub_entry = {
                'title': pub.get('name', ''),
                'authors': [basics.get('name', 'David Laing')]  # Always include author
            }
            
            # Add optional fields
            if pub.get('releaseDate'):
                pub_entry['date'] = pub['releaseDate']
            
            # Map publisher to journal field in RenderCV
            if pub.get('publisher'):
                pub_entry['journal'] = pub['publisher']
            
            # Add summary as part of the title or journal (RenderCV doesn't have a summary field)
            # We'll append summary to the journal field if both exist
            if pub.get('summary') and pub.get('publisher'):
                pub_entry['journal'] = f"{pub['publisher']} - {pub['summary']}"
            elif pub.get('summary') and not pub.get('publisher'):
                pub_entry['journal'] = pub['summary']
                
            rendercv_data['cv']['sections']['publications'].append(pub_entry)
    
    # Convert projects
    if projects:
        rendercv_data['cv']['sections']['projects'] = []
        for project in projects:
            project_entry = {
                'name': project.get('name', ''),
                'date': project.get('startDate', ''),
                'highlights': [project.get('description', '')] if project.get('description') else []
            }
            
            # Add project highlights if they exist
            if project.get('highlights'):
                project_entry['highlights'].extend(project['highlights'])
                
            rendercv_data['cv']['sections']['projects'].append(project_entry)
    
    # Convert skills to technologies (simplified)
    if skills:
        rendercv_data['cv']['sections']['technologies'] = []
        for skill in skills:
            tech_entry = {
                'label': skill.get('name', ''),
                'details': ', '.join(skill.get('keywords', []))
            }
            rendercv_data['cv']['sections']['technologies'].append(tech_entry)
    
    # Write YAML file
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(rendercv_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"Successfully converted {json_file} to {output_file}")

if __name__ == '__main__':
    # Default files
    json_file = 'static/resume.json'
    yaml_file = 'resume.yaml'
    
    # Accept command line argument for source file
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        sys.exit(1)
    
    convert_json_to_rendercv_yaml(json_file, yaml_file)