#!/usr/bin/env python3
"""
Extract evaluation flags for Intel based on research facts.
This script analyzes Intel's research data and generates evaluation flags.
"""

from wctf_core import WCTFClient
from datetime import date

def main():
    # Initialize client with stage-based path
    client = WCTFClient(data_dir="./data/stage-1")

    # Get Intel's facts
    facts_result = client.get_facts("Intel")
    if not facts_result['success']:
        print(f"Error: {facts_result['message']}")
        return

    facts = facts_result['facts']
    print(f"Analyzing {facts['total_facts']} facts for Intel...")
    print(f"Research date: {facts['research_date']}")
    print(f"Information completeness: {facts['information_completeness']}")

    # Based on the framework and facts, extract evaluation flags
    flags_yaml = """company: Intel
company_slug: intel
evaluation_date: 2025-10-22
evaluator_context: Senior Software Engineer evaluating opportunity for IC role with focus on technical excellence, organizational stability, and sustainable work environment

senior_engineer_alignment:
  organizational_maturity: POOR
  technical_culture: EXCELLENT
  compensation_competitiveness: POOR
  work_life_balance: GOOD
  growth_trajectory: POOR
  job_security: POOR
  engineering_investment: GOOD

green_flags:
  critical_matches:
    - flag: World-class technical culture with 19,000 software engineers and 700+ Intel Labs researchers
      impact: Access to cutting-edge technology work, deep technical expertise, and opportunity to work on foundational computing systems. Strongest open source contributor with 35+ year commitment.
      confidence: High - Explicit from research showing largest Linux contributor since 2007, 1,315 GitHub repos, 300+ OSS projects, $100M annual university research investment
    - flag: Excellent work-life balance ratings (4.0/5 on Glassdoor, 4.1/5 on Blind)
      impact: Sustainable work environment despite organizational challenges. Engineers consistently praise work-life balance in reviews.
      confidence: High - Explicit from multiple review platforms showing consistent 4.0+ ratings for work-life balance
    - flag: Significant government and strategic partner backing ($16.76B from CHIPS Act + US equity, $5B NVIDIA investment, $2B SoftBank)
      impact: Financial runway secured despite losses, indicating confidence from major stakeholders in Intel's long-term viability
      confidence: High - Explicit from Q2 2025 earnings and official announcements

  strong_positives:
    - flag: Strong engineering focus with C/C++/Python stack, oneAPI platform, and emphasis on open source
      impact: Modern technical stack with commitment to open standards and portability
      confidence: High - Explicit from Intel developer documentation and job postings
    - flag: Active technical community participation with 200+ academic papers annually and major conference presence
      impact: Opportunity for learning, professional development, and external visibility
      confidence: High - Explicit from Intel Labs publications and conference participation records
    - flag: Smart colleagues and collaborative teams frequently praised in reviews
      impact: Learning opportunities from experienced engineers despite organizational challenges
      confidence: Medium - Implied from aggregated employee reviews on Glassdoor, Blind, Indeed
    - flag: Comprehensive ISO certifications (14001, 45001, 9001, 27001, 50001) at all mature sites
      impact: Professional work environment with strong processes for safety, quality, and security
      confidence: High - Explicit from Intel Corporate Certifications Directory

red_flags:
  dealbreakers:
    - flag: Massive ongoing layoffs - 24,000 jobs (24% of workforce) cut by end of 2025, following 15,000 cuts in 2024
      impact: Extreme job insecurity, survivor guilt, constant organizational churn destroying team cohesion and institutional knowledge
      severity: YES
      confidence: High - Explicit from Q2 2025 earnings showing workforce reduction from 108,900 to target 75,000
    - flag: Historic financial losses - $18.8B loss in 2024 (largest in company history) with -$10.9B trailing free cash flow
      impact: Fundamental business model challenges threatening long-term viability despite government support
      severity: YES
      confidence: High - Explicit from Q4 2024 and Q2 2025 earnings releases
    - flag: Catastrophic employee confidence - only 36% positive business outlook, 48% CEO approval rating
      impact: Internal recognition that company direction is broken, creating toxic atmosphere where best talent is actively seeking exits
      severity: YES
      confidence: High - Explicit from Glassdoor ratings showing significantly below-average outlook

  concerning:
    - flag: Fourth CEO in 7 years (Lip-Bu Tan started March 2025), major executive turnover including 30-year veterans departing
      impact: No strategic continuity, repeated strategy pivots, inability to execute long-term plans
      severity: YES
      confidence: High - Explicit from company announcements showing leadership instability pattern
    - flag: Mandatory 4-day RTO policy effective September 2025, increased from 3-day hybrid
      impact: Reduced flexibility for senior engineers, cited as factor in departures, CEO noted "uneven compliance" with previous policy suggesting enforcement culture
      severity: MAYBE
      confidence: High - Explicit from TechCrunch reporting on April 2025 announcement
    - flag: Foundry business losing $13B annually with breakeven not expected until 2027
      impact: Core strategic bet bleeding massive cash, creating pressure on other divisions
      severity: YES
      confidence: High - Explicit from Q4 2024 earnings and Manufacturing Dive reporting
    - flag: Below-market compensation compared to competitors, benefits reductions (sabbatical changes, perks eliminated)
      impact: Total compensation package not competitive with AMD, NVIDIA, cloud companies despite working at struggling company
      severity: MAYBE
      confidence: Medium - Implied from aggregated employee reviews mentioning comp concerns
    - flag: Market share erosion to AMD (36.5% servers) and NVIDIA dominance in AI
      impact: Losing competitive position in key growth markets, making turnaround harder
      severity: YES
      confidence: High - Explicit from Mercury Research data showing AMD gains and NVIDIA AI leadership
    - flag: Recurring themes of poor communication, frequent restructuring every 2 quarters
      impact: Constant organizational churn preventing focus on technical execution
      severity: MAYBE
      confidence: Medium - Implied from aggregated employee reviews on Glassdoor and Blind
    - flag: Removed from Dow Jones Industrial Average November 2024, replaced by NVIDIA
      impact: Symbolic of Intel's decline from blue-chip status to struggling turnaround
      severity: MAYBE
      confidence: High - Explicit from Wikipedia DJIA changes

missing_critical_data:
  - question: What is the specific team's coordination style and does it match what the turnaround demands?
    why_important: Intel needs orienteering/expedition coordination for turnaround, but may have established-route culture from decades of market dominance. Mismatch would cause execution failures regardless of strategy quality.
    how_to_find: Insider conversations about how decisions are made, how quickly teams can pivot, whether there's psychological safety to challenge direction
  - question: What is the realignment ability of the specific team you'd join?
    why_important: With 4 CEOs in 7 years and constant restructuring, teams MUST be able to realign faster than strategy changes. Low realignment ability means every pivot destroys team effectiveness.
    how_to_find: Ask insiders about recent pivots - how long did it take to realign? Were team members able to voice concerns? Did the team emerge stronger or more fragmented?
  - question: What is the retention rate for senior engineers on the specific team?
    why_important: If best engineers are leaving despite "good work-life balance," something is deeply broken. Retention signals whether this is a sustainable place to do meaningful work.
    how_to_find: Network research with current and former team members, LinkedIn tracking of team transitions
  - question: How does compensation actually compare for IC senior engineers vs AMD, NVIDIA, cloud companies?
    why_important: Reviews say "below market" but no specific data. Need to know if gap is 10% (tolerable for stability) or 30%+ (unsustainable).
    how_to_find: Levels.fyi data, negotiation conversations, insider compensation discussions
  - question: What is the actual scope of autonomy and technical decision-making for senior ICs?
    why_important: In restructuring/layoff environment, technical autonomy often gets centralized. Need to know if senior ICs can still make meaningful technical decisions.
    how_to_find: Insider conversations about recent technical decisions, architectural authority, ability to push back on bad directions
  - question: Which specific division/product group and what is their strategic importance?
    why_important: Intel Labs or Core CPU teams might be protected; other groups could face continued cuts. Strategic importance determines runway.
    how_to_find: Must be specified in offer, then validate through insider research about that group's funding and headcount trajectory

synthesis:
  mountain_worth_climbing: NO
  sustainability_confidence: LOW

  alignment_with_senior_engineer_values:
    organizational_maturity:
      rating: POOR
      rationale: Four CEOs in 7 years, constant restructuring, 24% workforce reduction, 36% positive business outlook. This is organizational chaos, not mature stability.

    technical_excellence:
      rating: EXCELLENT
      rationale: World-class technical culture, 19,000 software engineers, 700+ researchers, largest Linux contributor, strong open source commitment, $100M annual research investment. Technical foundation is genuinely excellent.

    work_sustainability:
      rating: POOR
      rationale: Despite good work-life balance ratings (4.0/5), the combination of massive layoffs, job insecurity, poor business outlook, and below-market comp creates unsustainable psychological environment. Survivor guilt and constant uncertainty drain energy regardless of hours worked.

    growth_potential:
      rating: POOR
      rationale: Career advancement limited (reviews cite this), company losing market share, strategic direction unclear. Even if individual learns a lot, resume value of "Intel 2025-2027" during turnaround period may be negative.

  the_five_elements:
    mountain_range:
      assessment: Hostile terrain
      details: Macro environment is brutal - $18.8B loss, -$10.9B free cash flow, foundry bleeding $13B annually, market share eroding to AMD/NVIDIA. Government support provides runway but doesn't change fundamental competitive disadvantage in AI era.

    chosen_peak:
      assessment: Unclear destination
      details: Four CEOs in 7 years means four different strategic directions. Current CEO (Lip-Bu Tan) started March 2025 - too new to assess if organization has truly aligned on his vision. Signs of misalignment (poor employee outlook, executive departures).

    coordination_style_match:
      assessment: Unknown but concerning
      details: Intel needs orienteering coordination (navigating turnaround in unknown terrain) but decades of market dominance likely created established-route culture. No evidence of fast realignment ability despite urgent need. Mandatory 4-day RTO suggests command-and-control vs trust-based coordination.

    rope_team_confidence:
      assessment: Team doesn't believe
      details: 36% positive business outlook, 48% CEO approval, "constant threat of job cuts" in reviews. This rope team is climbing because they're contractually obligated, not because they believe in reaching the summit. Mutual belief is absent.

    daily_climb:
      assessment: Death march, not energizing journey
      details: Despite good work-life balance hours, the daily reality is surviving layoffs, watching colleagues cut, working with below-market comp, in constant organizational churn. Reviews describe fear, not excitement. The 99 days would be psychologically draining.

  coordination_style_evaluation:
    what_terrain_demands: Orienteering + Expedition hybrid - navigating turnaround (unknown path) while coordinating across massive organization (can't move alpine-fast with 75,000 people)

    likely_current_style: Established Route culture trying to do Expedition coordination - decades of market dominance created "execute the roadmap" mindset, now attempting heavy process coordination for turnaround but without agility

    mismatch_consequences: Bureaucracy preventing fast pivots when terrain changes, but also insufficient trust/context for teams to navigate autonomously. Worst of both worlds.

    realignment_ability_signals:
      communication_bandwidth: LOW - Massive layoffs and 4-day RTO reduce time for coordination
      decision_authority: UNKNOWN - Need insider validation of technical decision authority
      shared_context: FRAGMENTED - High turnover and restructuring destroy shared vocabulary
      psychological_safety: LOW - 36% outlook, layoff fear mean people won't challenge bad directions
      information_transparency: UNKNOWN - Need insider validation
      practiced_pivots: HIGH FREQUENCY, LOW SUCCESS - Many pivots (4 CEOs) but poor outcomes

    realignment_verdict: Realignment ability appears inadequate for pace of terrain changes, creating death spiral where each strategic shift further degrades team effectiveness

  the_gut_check:
    would_i_tell_mom: "No. Can't explain why joining a struggling company with massive layoffs, historic losses, and lowest employee confidence in industry would be a good decision. Technical work is excellent but mountain is collapsing."

    99_days_vision: Watching talented colleagues get laid off every quarter, working with below-market comp while executives get millions, spending 4 days/week in office watching morale crater, trying to do excellent technical work while organization churns around you

    is_this_energizing: No. This is survival mode, not growth mode. Even with great immediate team, the organizational chaos and job insecurity would be psychologically draining.

  verdict_for_senior_engineer: |
    HARD PASS for senior IC role.

    Intel offers genuinely excellent technical work - world-class engineering culture, cutting-edge systems, brilliant colleagues, strong open source commitment. If this were 2020 Intel, it would be an outstanding opportunity.

    But in 2025, you'd be joining during organizational collapse:
    - 24% workforce reduction ongoing (24,000 jobs by end of 2025)
    - $18.8B historic loss with -$10.9B free cash flow
    - 4th CEO in 7 years, major executive exodus
    - 36% employee business outlook (they don't believe in the turnaround)
    - Below-market compensation while company loses money
    - Mandatory 4-day RTO during cost-cutting

    The mountain range (macro environment) is hostile, the chosen peak (strategy) keeps changing with each CEO, the rope team (employees) doesn't believe in success, and the daily climb (work reality) is surviving layoffs rather than building something meaningful.

    Most critically: Even if you personally don't get laid off, spending 2-3 years watching talented colleagues get cut every quarter, working with survivor guilt and job insecurity, for below-market comp, will drain your energy and damage your mental health. The opportunity cost vs. working somewhere stable and growing is massive.

    The technical work is legitimately excellent, but excellent technical work in an organizationally collapsing company is a trap. Your resume in 2027-2028 will say "Intel during the turnaround years" which may be neutral at best.

    EXCEPTION: Could consider if (1) Specific role is Intel Labs with protected funding, (2) Compensation negotiated to market (or above to compensate for risk), (3) Remote exception granted, (4) Insider validation that specific team has high retention and strategic importance, (5) You're explicitly optimizing for learning specific technical domain over career growth and stability.

    Otherwise: Too much organizational risk, too little upside. Find a mountain worth climbing with a team that believes they can summit.

  confidence_in_assessment: HIGH

  information_quality: Excellent - 107 facts with high information completeness from Q2 2025 earnings, multiple employee review platforms, recent news coverage through October 2025

  key_assumptions:
    - Government support ($16.76B) provides runway but doesn't fix fundamental business model
    - Employee sentiment (36% outlook) accurately reflects internal reality
    - Leadership instability (4 CEOs in 7 years) predicts continued strategic inconsistency
    - Massive layoffs (24% workforce) create unsustainable work environment regardless of hours
    - Technical culture strength can't compensate for organizational collapse

  what_would_change_assessment:
    - Evidence of actual strategic alignment across organization (not just CEO statements)
    - Significant improvement in employee outlook (to 50%+ positive)
    - Specific team/role with demonstrated protection from cuts and high retention
    - Compensation significantly above market to compensate for risk (20%+ premium)
    - Remote work exception or 3-day RTO maximum
    - New CEO (Lip-Bu Tan) demonstrating effective turnaround execution for 12+ months
"""

    # Save the flags
    print("\nSaving evaluation flags...")
    result = client.save_flags("Intel", flags_yaml)

    if result['success']:
        print(f"\n✓ Success: {result['message']}")
        print(f"  Company: {result['company_name']}")
        print(f"  File: {result['file_path']}")
        print(f"  Operation: {result['operation']}")
    else:
        print(f"\n✗ Error: {result['message']}")
        if 'error' in result:
            print(f"  Details: {result['error']}")

if __name__ == "__main__":
    main()
