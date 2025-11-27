#!/usr/bin/env python3
"""Example: Search roles for company with existing orgmap."""

from wctf_core import WCTFClient


def main():
    client = WCTFClient()

    # Example: Search roles for company with known orgmap
    company = "ExampleCorp"

    # Get orgmap context for targeted search
    orgmap = client.get_orgmap(company)
    if orgmap["success"]:
        print(f"Targeting search based on {orgmap['orgmap']['total_peaks']} peaks")
        print(f"Known tech focus: {orgmap['orgmap']['peaks'][0]['tech_focus']}")

    # Example role data that would be saved
    roles_yaml = """
company: "ExampleCorp"
last_updated: "2025-11-27"
search_metadata:
  sources: ["company careers", "LinkedIn"]
  last_search_date: "2025-11-27"
peaks:
  - peak_id: "cloud_services"
    peak_name: "Cloud Services"
    roles:
      - role_id: "202511_senior_swe_k8s"
        title: "Senior Software Engineer, Kubernetes"
        url: "https://examplecorp.com/careers/12345"
        posted_date: "2025-11-27"
        location: "Remote"
        rope_team_id: "platform_infrastructure"
        rope_team_name: "Platform Infrastructure"
        seniority: "senior_ic"
        description: "Build and maintain Kubernetes infrastructure"
        requirements: ["5+ years K8s", "Go experience", "Cloud knowledge"]
        wctf_analysis:
          analyzed_date: "2025-11-27"
          coordination_style: "established"
          terrain_match: "good_fit"
          mountain_clarity: "clear"
unmapped_roles: []
"""

    # Save roles using SDK
    result = client.save_roles(company, roles_yaml)

    if result["success"]:
        roles = result["roles"]
        print(f"Roles saved to: {result['path']}")
        print(f"Total roles: {roles['total_roles']}")
        print(f"Mapped roles: {roles['mapped_roles']}")
        print(f"Unmapped roles: {roles['unmapped_count']}")
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
