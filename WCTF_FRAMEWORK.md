# WCTF Framework: Worth Climbing Together Framework

## Philosophy

**Worth Climbing Together Framework (WCTF)** is an evaluation framework for senior engineers assessing job opportunities. It treats job evaluation as **mountaineering expedition planning** - recognizing that success requires more than just a viable business model. You need the right mountain, the right team, sustainable daily conditions, and a story you'll be proud to tell.

The framework deliberately **avoids mechanical scoring**. There are no perfect companies, only trade-offs. The goal is to surface signals that inform your gut decision, not to produce a calculated "hire/no-hire" score.

## The Mountain Metaphor

Every job opportunity is like planning a mountain expedition. Success depends on five elements working together:

### 1. Mountain Range: Macro Environment
**"Can *any* team succeed here?"**

Before evaluating a specific team, ask whether the broader business environment is viable. Are the company's finances sustainable? Is the market position defensible? Can the business model support long-term employment?

This isn't about picking winners or predicting IPOs. It's about **avoiding mountains that are actively crumbling** - companies burning cash with no path to sustainability, shrinking markets with no defensible moat, or business models fundamentally broken by external forces.

**Key Questions:**
- Is the business financially viable? (profitability, runway, funding)
- Is the market position defensible? (competitors, market share, growth trends)
- Is the company stable enough to support multi-year career investment?

**Green Flags:**
- Profitable with healthy margins
- Strong customer retention
- Growing or stable market position
- Clear path to sustainability

**Red Flags:**
- Burning cash with unclear path to profitability
- Shrinking market share or failing business model
- Frequent layoffs despite growth claims
- Financial instability creating existential risk

### 2. Chosen Peak: Strategic Alignment
**"Is everyone climbing the *same* mountain?"**

Does the organization have clarity about what it's building and why? Are engineering, product, and business aligned on goals? Is there a coherent technical strategy, or are teams pulling in different directions?

This dimension evaluates whether the company treats **technology as strategic differentiator** vs cost center to optimize. Are technical decisions driven by strategic vision or quarterly cost pressure?

**Key Questions:**
- Is there clear product strategy and technical vision?
- Do engineering and product work as partners or adversaries?
- Is technology positioned as strategic asset or expense to minimize?
- Are teams building the right things with the right approach?

**Green Flags:**
- Clear technical vision aligned with business strategy
- Engineering has seat at strategic table
- Investment in technical excellence and innovation
- Modern practices and tooling (CI/CD, DORA metrics, developer productivity)

**Red Flags:**
- No coherent technical strategy or frequent pivots
- Engineering treated as order-taker, not strategic partner
- Cost-cutting undermines technical investment
- Legacy technical debt constraining innovation
- Lack of deployment velocity or modern practices

### 3. Rope Team Confidence: Mutual Belief
**"Does the team believe they can succeed *together*?"**

Mountaineering requires trust in your rope team - the people literally holding your safety line. Similarly, job success requires believing in your colleagues and leadership.

This evaluates **organizational trust and stability**. Do people believe in the leadership? Is there psychological safety? Do teammates support each other, or is it political infighting? Is there stability or constant churn?

**Key Questions:**
- Do you trust the leadership's judgment and integrity?
- Is there psychological safety and team cohesion?
- Are teammates competent and collaborative?
- Is the organization stable or constantly reorganizing?

**Green Flags:**
- Strong leadership with clear track record
- High employee satisfaction and low attrition
- Collaborative culture with psychological safety
- Organizational stability and long tenure

**Red Flags:**
- Poor leadership reputation or low CEO approval
- High attrition or frequent reorganizations
- Political culture or blame-oriented environment
- Low employee satisfaction scores
- Recent layoffs creating trust issues

### 4. Daily Climb: Work Reality
**"Will the 99 days be energizing or draining?"**

Most of your time won't be at the summit celebrating. It'll be the daily grind of the climb. Is that daily experience sustainable and energizing, or will it drain you?

This evaluates **work-life sustainability, compensation, and daily working conditions**. Can you sustain this pace? Is compensation fair? Are policies reasonable? Is there on-call burden or burnout risk?

**Key Questions:**
- What are typical working hours and work-life balance?
- Is compensation competitive and fair?
- Are policies (remote, hybrid, PTO) reasonable?
- Is there on-call burden or operational toil?
- Can you sustain this pace long-term?

**Green Flags:**
- Sustainable working hours and good work-life balance
- Competitive total compensation
- Flexible policies (remote, hybrid) that work for your situation
- Reasonable on-call and operational burden
- Career growth paths and development support

**Red Flags:**
- Chronic overwork or burnout culture
- Below-market compensation or poor equity terms
- Inflexible policies incompatible with life needs
- Heavy on-call burden or constant firefighting
- No career progression or development support

### 5. Story Worth Telling: The Mom Test
**"Would you be proud to explain this work to your mom?"**

In five years, when explaining what you did, will you feel proud? Does this build a career narrative you want? Is the work meaningful and the brand valuable?

This is the **"Mom Test"** - not whether your mom would understand the technical details, but whether you'd feel good explaining the mission, impact, and what you accomplished.

**Key Questions:**
- Does this work align with your values and interests?
- Will this build skills and resume value you want?
- Is the company brand and mission something you're proud of?
- Will you have meaningful impact and ownership?
- Does this advance your long-term career narrative?

**Green Flags:**
- Mission and values aligned with your priorities
- Strong brand value and resume credibility
- Meaningful impact and real ownership
- Skills development in areas you care about
- Work you'd be excited to explain and showcase

**Red Flags:**
- Mission misaligned with your values
- Weak brand or questionable company reputation
- Limited impact or ownership (support role vs builder)
- Skills stagnation or narrow technology exposure
- Work you'd rather not discuss or downplay

## Two-Layer Investigation Approach

WCTF evaluation happens in two layers:

### Layer 1: Macro Environment Research
**5-15 minutes of automated research** using public sources:
- Company financials, funding, growth metrics
- Market position, competitors, analyst reports
- Organizational news (layoffs, leadership changes, expansions)
- Technical culture indicators (blog, GitHub, StackShare, Glassdoor)

This creates `company.facts.yaml` - structured facts with sources and confidence levels.

**Goal:** Quickly surface obvious red flags and establish baseline understanding.

### Layer 2: Insider Reality Validation
**Ongoing conversations** with current/former employees:
- Validate or invalidate Layer 1 findings
- Understand ground truth vs public narrative
- Surface cultural nuances and team dynamics
- Get insider perspective on what it's really like

This creates `company.insider.yaml` - firsthand accounts from people who've experienced the reality.

**Goal:** Go beyond PR and marketing to understand actual working conditions and team reality.

## Flag-Based Evaluation Philosophy

### No Mechanical Scoring
WCTF **does not** produce a numerical score or automated recommendation. Why?

1. **Context matters** - The same fact can be green or red depending on your situation
2. **Trade-offs are inevitable** - No perfect company exists; you're choosing which imperfections you can accept
3. **Gut decisions are valid** - After surfacing signals, trust your intuition
4. **Individual priorities vary** - What's critical for one person may be negotiable for another

### Green Flags & Red Flags
Instead of scores, collect **flags** - signals that inform your decision:

**Green Flags** = Positive indicators
- Critical matches: Non-negotiable requirements met
- Strong positives: Significant advantages
- Nice to have: Bonus factors

**Red Flags** = Concerning signals
- Dealbreakers: Non-negotiable requirements violated
- Concerning: Significant disadvantages
- Worth investigating: Potential issues needing validation

**The same fact can be different colors:**
- "Hybrid 3 days/week" = Green flag if you live locally, Red flag if you don't
- "Fast growth" = Green flag if you want equity upside, Red flag if you want stability
- "Startup" = Green flag if you want ownership, Red flag if you need financial security

### Synthesis Over Summation
The framework encourages **synthesizing tensions** rather than tallying flags:
- "Profitable but laying off" - What does this mean?
- "Great mission but poor leadership" - Can you accept this trade-off?
- "High compensation but weak culture" - What matters more to you?

Present the evidence and tensions objectively. Let the evaluator make informed decisions based on their priorities.

## Evaluator Values & Priorities

WCTF is designed for **senior engineers with 15-25 years experience** who value:

1. **Autonomy & Ownership** - Want to drive decisions, not just execute orders
2. **Technical Excellence** - Care about engineering quality, velocity, and modern practices
3. **Sustainability** - Need work-life balance and long-term career stability
4. **Meaningful Impact** - Want work that matters and aligns with values
5. **Team Quality** - Prefer working with strong, collaborative teammates
6. **Career Narrative** - Building resume value and skills for future opportunities

Your personal values may differ! Adapt the framework to emphasize what matters to you.

## Using the Framework

### Step 1: Layer 1 Research
Use `/research` tools or scripts to collect public facts. Focus on:
- Obvious red flags (failing business, toxic culture, layoffs)
- Strong green flags (profitable, growing, high satisfaction)
- Missing information that needs insider validation

### Step 2: Extract Flags
Review facts and identify:
- Which dimension each flag belongs to
- Whether it's green (positive) or red (concerning)
- Impact and confidence level

### Step 3: Insider Conversations
Use `/interview-guide` to prepare structured questions that:
- Validate low-confidence facts
- Fill knowledge gaps
- Understand ground truth vs marketing

### Step 4: Synthesize & Decide
Use `/evaluation-rubric` to create analytical synthesis:
- Review all evidence across five dimensions
- Identify tensions and trade-offs
- Consider what matters most to you
- Make informed gut decision

**Remember:** There are no perfect companies. You're choosing which mountain to climb and which imperfections you can accept.

## Framework Evolution

WCTF is a living framework. It evolves based on:
- New evaluation experiences and lessons learned
- Changing industry dynamics (remote work, AI tools, market conditions)
- Individual evaluator priorities and values

The core philosophy remains: **Surface signals, identify tensions, support informed gut decisions.** No mechanical scoring, no prescriptive recommendations, just structured research informing human judgment.

---

**Worth Climbing Together Framework** - Success in any endeavor requires climbing together as a team. The framework helps you evaluate whether this is a mountain worth climbing with this particular team.
