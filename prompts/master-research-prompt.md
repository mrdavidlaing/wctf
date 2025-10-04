# Master Research Prompt Template

I need to assess the macro environment for [COMPANY NAME] to understand if even a great team could succeed there. 

YOU MUST RETURN YOUR RESPONSE IN YAML FORMAT ONLY. NO MARKDOWN, NO NARRATIVE TEXT.

Search for information in these areas:

FINANCIAL HEALTH:
- Latest funding round (amount, valuation, date, investors)
- Runway and burn rate if available
- Revenue growth metrics (YoY, MRR/ARR if applicable)
- Profitability status or path to profitability timeline
- Any layoffs in past 18 months (percentage, dates, departments affected)
- Customer concentration (if publicly known)

MARKET POSITION:
- Main product/service offering (in simple terms)
- Primary competitors and market position
- Total addressable market size and growth rate
- Customer reviews on G2, Capterra, Gartner, or similar (aggregate scores)
- Recent product launches or pivots
- Key differentiators or moats

ORGANIZATIONAL STABILITY:
- Current CEO and CTO/VP Engineering (tenure, background)
- Executive changes in past 24 months
- Current headcount and hiring velocity (LinkedIn data)
- Glassdoor rating specifically for engineering (if available)
- Office locations and remote work policy

TECHNICAL CULTURE:
- Tech stack (from job postings, engineering blog, StackShare)
- Engineering blog activity (frequency, technical depth)
- Open source contributions (GitHub org activity)
- Conference talks or technical publications by employees
- AI/ML adoption stance (from job postings or statements)

SEARCH THESE SOURCES:
- News: TechCrunch, The Information, Reuters, Bloomberg
- Company: Their blog, press releases, investor relations
- Reviews: Glassdoor, Blind (teamblind.com), G2, Capterra
- Technical: Engineering blog, GitHub, StackOverflow Jobs
- Financial: Crunchbase, PitchBook, SEC filings (if public)
- Social proof: LinkedIn company page, employee count changes
- Forums: Hacker News, relevant Reddit communities

===MANDATORY OUTPUT FORMAT - USE THIS EXACT YAML STRUCTURE===

company: "[COMPANY NAME]"
research_date: "[TODAY'S DATE as YYYY-MM-DD]"

financial_health:
  facts_found:
    - fact: "[specific factual statement without interpretation]"
      source: "[exact publication/website name]"
      date: "[YYYY-MM-DD when source was published]"
      confidence: "[must be: explicit_statement OR implied OR inferred]"
    # repeat for each fact found
  
  missing_information:
    - "[specific data point that could not be found]"
    # repeat for each missing item

market_position:
  facts_found:
    - fact: "[specific factual statement]"
      source: "[publication name]"
      date: "[YYYY-MM-DD]"
      confidence: "[explicit_statement OR implied OR inferred]"
    # repeat for each fact
  
  missing_information:
    - "[what wasn't found]"
    # repeat for each missing item

organizational_stability:
  facts_found:
    - fact: "[specific factual statement]"
      source: "[publication name]"
      date: "[YYYY-MM-DD]"
      confidence: "[explicit_statement OR implied OR inferred]"
    # repeat for each fact
  
  missing_information:
    - "[what wasn't found]"
    # repeat for each missing item

technical_culture:
  facts_found:
    - fact: "[specific factual statement]"
      source: "[publication name]"
      date: "[YYYY-MM-DD]"
      confidence: "[explicit_statement OR implied OR inferred]"
    # repeat for each fact
  
  missing_information:
    - "[what wasn't found]"
    # repeat for each missing item

summary:
  total_facts_found: [integer count of all facts]
  information_completeness: "[must be: high OR medium OR low]"
  most_recent_data_point: "[YYYY-MM-DD of newest fact]"
  oldest_data_point: "[YYYY-MM-DD of oldest fact]"

===END MANDATORY FORMAT===

CRITICAL REQUIREMENTS - FAILURE TO FOLLOW THESE WILL MAKE YOUR RESPONSE UNUSABLE:
1. OUTPUT MUST BE VALID YAML - no markdown headers, no narrative text
2. Use exact field names: "facts_found" and "missing_information" 
3. Every fact MUST have all 4 fields: fact, source, date, confidence
4. Confidence MUST be exactly one of: explicit_statement, implied, or inferred
5. Dates MUST be in YYYY-MM-DD format
6. Include ALL categories even if facts_found is empty (use empty list [])
7. Do NOT include any text outside the YAML structure
8. Do NOT add interpretation or commentary - only verifiable facts
9. Remove any citation artifacts or reference markers from facts
10. Keep facts atomic - one piece of information per fact entry
11. For dates, use the source publication date, not access date
12. If multiple sources confirm same fact, list once with most authoritative source

DO NOT WRITE ANYTHING BEFORE OR AFTER THE YAML OUTPUT.
START YOUR RESPONSE WITH: company: "[COMPANY NAME]"
