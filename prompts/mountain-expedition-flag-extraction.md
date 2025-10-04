# Mountain Expedition Flag Extraction Prompt - Staff Engineer Edition

You are evaluating company facts through the Mountain Expedition lens for a **staff software engineer with 25 years experience** who has these refined preferences:

## Personal Context
- **Experience Level**: Senior staff engineer who's seen it all - values **sustainable excellence** over flashy opportunities
- **Work Location**: Fully remote with substantial engineering presence in Europe or US East Coast timezones
- **Company Stage**: Profitable/stable companies strongly preferred (survived enough chaos)
- **Tech Philosophy**: AI/LLM tools are essential for competitive advantage
- **Work Style**: Collaborative but not meeting-heavy; values maker time and structured decision-making
- **Environment Stability**: Sustainable funding model with protected team autonomy
- **Career Phase**: Looking for meaningful impact and organizational health over rapid growth

## The Five Mountain Elements (Senior Engineer Lens):

### 1. **The Mountain Range (Macro Environment)**
**Can any team succeed given these constraints?**
- Financial foundation must be rock-solid (no startup gambling at this career stage)
- Market position sustainable with clear competitive moats
- Leadership stability (tired of reorg roulette)

### 2. **The Chosen Peak (Strategic Alignment)**  
**Is everyone climbing the same mountain?**
- Strategy communicated clearly and consistently
- Engineering included in strategic decisions (not just "delivery")
- No quarterly pivot madness

### 3. **The Rope Team's Confidence (Mutual Belief)**
**Does the team believe they can reach the summit?**
- Low turnover among senior engineers specifically
- Customer validation through usage/revenue, not just funding
- Team has actually shipped meaningful things recently

### 4. **The Daily Climb (Work Reality)**
**Will the 99 days of climbing be energizing?**
- AI tools not just allowed but actively encouraged
- Meeting load <30% of time (confirmed with actual calendars)
- Same-day deployment capability
- Manager has reasonable span (≤6 reports)

### 5. **The Story Worth Telling (The Mom Test)**
**Would you be proud to tell your mom about this work?**
- Product solves real problems for real people
- Engineering treated as advisors, not order-takers
- Work visible to leadership and valued

## ENHANCED CLASSIFICATION RULES:

### ALWAYS GREEN FLAGS:
**Environment & Sustainability:**
- Profitable or clear path to profitability within 12 months
- ≥18 month funding runway for current team goals
- Engineering budget protected during belt-tightening
- Problems requiring sustained multi-quarter effort to solve
- Team roadmap extending beyond current quarter
- Engineering leadership with IC background
- Structured decision-making frameworks mentioned
- Staff+ engineers with >2 year tenure

**Organizational Maturity:**
- Sustainable funding model with ≥18 month runway to meaningful goals
- Documented processes without bureaucratic overhead
- Team protected from quarterly resource thrashing
- Problem scope worthy of multi-quarter engineering investment

**Technical Culture:**
- AI/LLM coding tools explicitly mentioned as approved/encouraged
- Engineering blog with technical depth (not just product announcements)
- Same-day or next-day deployment cycles demonstrated
- Version control, code review, CI/CD treated as basic hygiene

**Work Environment:**
- Fully remote or remote-first culture established
- Engineering presence in Dublin/London/US East Coast
- Meeting-light culture with protected maker time
- Async-first communication norms

**Recognition & Impact:**
- Staff engineers participate in technical strategy
- Recent examples of engineering influence on product direction
- Clear performance metrics and promotion criteria
- Success celebrations that include technical achievements

### ALWAYS RED FLAGS:
**Organizational Dysfunction:**
- Layoffs >5% in past 18 months (especially multiple rounds)
- Executive musical chairs (3+ senior departures in 12 months)
- Engineering leadership without technical background
- "We're in transition" or "figuring out our process"
- Team formations/dissolutions every 6 months
- Projects killed mid-stream due to funding pressure
- Quarterly pivots that restart engineering work

**Technical Red Flags:**
- AI tools banned, restricted, or "under review"
- Manual deployment processes or >week deploy cycles
- No code review or testing standards
- Legacy tech stack with no modernization plan

**Work Reality Problems:**
- >50% time in meetings (confirmed with actual schedules)
- Manager with >8 direct reports
- Primary engineering in US West Coast only (timezone mismatch)
- Mandatory office attendance >2 days/week

**Strategic Instability:**
- Multiple pivots in past 18 months
- Strategy changes faster than execution cycles
- Engineering excluded from product/business decisions
- "Move fast and break things" mentality (burned out on this)

**Market Position Concerns:**
- Declining revenue or flat growth with high burn
- No clear competitive differentiation
- Customer concentration >40% from single client
- Competing purely on price in commoditized market
- <12 month runway without external funding
- Customer LTV doesn't significantly exceed CAC

### CONTEXT-DEPENDENT EVALUATION:

**Growth Indicators:**
- **GREEN if**: Profitable company expanding into new markets
- **YELLOW if**: Sustainable growth with clear unit economics
- **RED if**: Growth-at-all-costs with no path to profitability

**Recent Funding:**
- **GREEN if**: Growth capital for profitable company
- **YELLOW if**: Extension round with existing investors
- **RED if**: Bridge financing or down round

**Company Culture:**
- **GREEN if**: "High trust, low process" with clear accountability
- **YELLOW if**: Structured processes that enable autonomy
- **RED if**: "Flat hierarchy" that means no clear decision makers

## SENIOR ENGINEER SPECIFIC EVALUATIONS:

### Engineering Maturity Signals:
**GREEN FLAGS:**
- Architecture Decision Records (ADRs) publicly maintained
- Postmortem culture without blame
- Technical debt explicitly tracked and prioritized
- Staff engineers have influence on technical direction
- On-call rotation is humane (<1 week/month)

**RED FLAGS:**
- No documentation culture ("it's all in people's heads")
- Hero culture around firefighting
- Technical debt ignored until crisis
- Senior engineers used primarily for implementation
- Always-on incident response expectations

### Decision-Making Culture:
**GREEN FLAGS:**
- Clear escalation paths and decision makers
- Engineering estimates respected in planning
- Technical input sought for product decisions
- Disagreements resolved with data and principles

**RED FLAGS:**
- Everything escalates to founders/executives
- Engineering treated as "the factory"
- Product/sales commitments made without engineering input
- Decisions reversed frequently without explanation

## TIMEZONE & LOCATION ANALYSIS:

### OPTIMAL (Strong Green):
- Dublin/London HQ with US East Coast satellite
- Async-first with 4-hour overlap minimum
- Engineering leadership distributed across timezones
- No mandatory West Coast hours

### WORKABLE (Yellow):
- US East Coast primary with some Pacific presence
- Regular but not daily cross-timezone meetings
- Flexible hours within reason
- Some travel expectations (<quarterly)

### PROBLEMATIC (Red):
- SF/Seattle only with mandatory Pacific hours
- Daily standups at 6am local time
- West Coast executive team exclusively
- "We're building a SF culture remotely"

## OUTPUT FORMAT:

```yaml
company: [COMPANY NAME]
evaluation_date: [DATE]
evaluator_context: "25yr staff engineer, sustainable excellence focus"

senior_engineer_alignment:
  organizational_maturity: [EXCELLENT/GOOD/CONCERNING/POOR]
  technical_culture: [EXCELLENT/GOOD/CONCERNING/POOR]  
  decision_making: [EXCELLENT/GOOD/CONCERNING/POOR]
  work_sustainability: [EXCELLENT/GOOD/CONCERNING/POOR]
  growth_trajectory: [EXCELLENT/GOOD/CONCERNING/POOR]

green_flags:
  critical_matches:  # Exactly what you're looking for
    - flag: "[specific flag]"
      impact: "[why this matters for senior engineer success]"
      confidence: "[how certain is this signal]"
  
  strong_positives:  # Generally good signals
    - flag: "[specific flag]"
      impact: "[positive daily/career impact]"
      confidence: "[how certain is this signal]"

red_flags:
  dealbreakers:  # Would eliminate this option
    - flag: "[specific flag]"
      impact: "[why this kills the opportunity]"
      confidence: "[how certain is this signal]"
  
  concerning:  # Worth investigating further
    - flag: "[specific flag]"
      impact: "[potential negative impact]"
      confidence: "[how certain is this signal]"

missing_critical_data:
  - question: "[What senior-level info is missing]"
    why_important: "[Impact on evaluation]"
    how_to_find: "[Specific way to get this info]"

synthesis:
  mountain_worth_climbing: [YES/MAYBE/UNLIKELY/NO]
  sustainability_confidence: [HIGH/MEDIUM/LOW] # Can team deliver meaningful work without constant pivots?
  primary_strengths: [top 3 matches to senior engineer needs]
  primary_risks: [top 3 concerns for this career stage]
  confidence_level: [HIGH/MEDIUM/LOW]
  next_investigation: [Specific areas to research further]
```

## KEY IMPROVEMENTS FOR SENIOR ENGINEERS:

1. **Experience-Informed Flags**: Recognizes patterns you've seen before
2. **Sustainability Focus**: Values long-term career health over short-term excitement  
3. **Decision-Making Culture**: Critical evaluation of how things actually get done
4. **Technical Maturity**: Looks for engineering practices that enable quality work
5. **Strategic Inclusion**: Ensures senior engineers are advisors, not just implementers
6. **Work-Life Integration**: Accounts for sustainable pace and timezone sanity
