/* ════════════════════════════════════════════════════════════════
   JAM Intelligence — shared article data + card renderer
   Loaded via <script src="articles.js"> by index.html, insight.html,
   insights.html and the per-sector listing pages.

   PUBLISHING A NEW ARTICLE (Workflow 1):
   add one entry at the TOP of ARTICLES — object insertion order is
   display order (newest first). The card then appears automatically
   on the homepage, the insights hub, its sector listing page and
   related grids. No other file needs editing.
   ════════════════════════════════════════════════════════════════ */

const SECTORS = {
  ai: {
    num: 'Sector A — 01',
    name: 'AI Transformation for SMEs',
    page: 'insights_ai.html',
    standfirst: "A marathon race needs mental and physical preparation. AI transformation demands the same discipline — not excitement about the destination, but honest preparation for what the journey actually costs."
  },
  eu: {
    num: 'Sector B — 02',
    name: 'EU Tech and Economics Landscapes',
    page: 'insights_eu.html',
    standfirst: "Political intent is not resource allocation. Financial services AI, life sciences, and regulatory expertise are Europe's natural positions in the AI value chain."
  },
  energy: {
    num: 'Sector C — 03',
    name: 'Energy & AI Buildout',
    page: 'insights_energy.html',
    standfirst: "Whoever controls the energy distribution layer of AI has a structural advantage that pure software companies cannot replicate. Energy is the binding constraint."
  }
};

const ARTICLES = {
  'ai-stress-points-capital': {
    tag: 'AI Transformation',
    sectorKey: 'ai',
    date: '1 Jul 2026',
    read: '8 min read',
    title: "AI's Three Stress Points in Capital Markets",
    dek: "One disruption, three balance sheets. The AI bubble is treated as one question; it is really real-economy software disruption transmitting into three capital-market structures that absorb it differently and in sequence.",
    body: [
      { t: 'lead', x: "The public IPO window gates private-equity exits; credit conditions gate refinancing for both. The noise is loudest where the danger is least — public equity; the real systemic transmitter is credit." },
      { t: 'h2', x: "1. Public equity — concentration misread as a bubble" },
      { t: 'p', x: "Recent selloffs revived the bubble chorus, but the move was a positioning unwind, not a demand collapse: Micron guided to $50bn revenue (16% above consensus) on 16 contracts worth ~$100bn to 2030, and Apple's price hike reflects memory-cost pass-through, not slowing demand. Russell 1000 Growth trades at a P/E of 22 sitting at the bottom 30% of its 10-year range, so the de-rating is done, and over $1T of buybacks make corporates net buyers." },
      { t: 'p', x: "The real flag is dispersion, not valuation: a concentrated, hyperscaler-led tape where single-stock volatility hides beneath a calm index (the Mag 7 fell 10% in June, turning into the “Lag Seven”). The unproven profitability sits with the user, not the builder: the rally prices the chipmakers' real profits, while the 29% hyperscaler cash-return measures selling compute, not enterprises earning a return deploying it (Salesforce: 8–9% organic). Leadership is already broadening to equal-weight, small caps and cyclicals, as the AI trade's rate of change peaks." },
      { t: 'h2', x: "2. Private equity — the exit machine seizes" },
      { t: 'p', x: "Around 30% of PE sits in software, the cohort most exposed to AI disruption, and the symptoms are in the plumbing: DPI is gummed at 8–10% against a 15–20% norm, holding periods have stretched to 7 years, and executives are borrowing against personal carry (broker Enness Global reports inquiries up threefold). Part distress, part conviction financing the wait." },
      { t: 'p', x: "The R1000G de-rating and OpenAI's delayed IPO keep the exit window shut. Medallia is the template: Thoma Bravo refused fresh equity and handed the business to Blackstone-led creditors, signalling the first major AI-driven software-LBO write-off. It crystallises PE losses, tests private credit, and threatens broader write-downs as private marks catch down to weaker public comparables." },
      { t: 'h2', x: "3. Credit — the transmitter, and where the real risk concentrates" },
      { t: 'p', x: "This is the leg to watch. Morgan Stanley flags an expected $500bn of AI-related debt issuance for 2026; the financing of the buildout is migrating from equity to debt, arriving faster than the market can absorb it, and the composition is deteriorating. The clearest sign: the hyperscalers, once prized as “bond-equivalents” — stable, cash-gushing, high-margin — are now selling debt to fund capex, a different and more fragile business model the equity market is actively repricing." },
      { t: 'p', x: "Debt now funds every layer of the stack: the chips (Apollo and Blackstone's $35bn private-credit package behind Broadcom), the labs (Anthropic's $35bn debt-funded buildout), launch and infrastructure (SpaceX's $25bn investment-grade bond), and the hardware vendors (HPE's $13bn customer-financing arm) — with high-yield and first-time data-centre issuance alone jumping from $0 last autumn to $40bn and heading toward $60bn." },
      { t: 'quote', x: "Co-existence holds only while the chain is fed by real cash flow; if it is fed by recycled capital, limited liquidity is the kill switch." },
      { t: 'p', x: "Three readings turn those numbers into a warning. First, the concentration is in the intermediaries, not just the issuers: the same sponsors financing the chip buildout are absorbing disrupted-software losses (Medallia) and issuing their own bonds — so the risk is correlated across one book, exactly the “circular financing” the BIS has now flagged. Second, the form of the debt is the tell: HPE lending customers money to buy HPE gear is vendor financing, the classic late-cycle move that manufactures demand out of debt. Third, backlog is only as good as its independence from the loop that created it: Nvidia's $1tn of revenue visibility reassures only if that demand is funded by real end-revenue, not by the same capital cycling through the system." },
      { t: 'h2', x: "4. Where it breaks, and where it resolves" },
      { t: 'p', x: "The chain has four roles: enablers (chip and compute winners), builders (hyperscalers and neo-clouds, free cash flow falling), monetisers (enterprise users whose ROI is still unproven), and financiers (the IPO, PE and private-credit machinery). These are not rivals but two ends of one flow — the market only rotates which end it rewards: enablers first on realised revenue, builders later on monetisation proof." },
      { t: 'p', x: "<strong>The directional call:</strong> public-equity stress is dispersion, not a bubble — the de-rating is done. Private equity is a slow grind: the exit backlog persists. Credit is where a rate or liquidity shock would actually cascade. Watch the credit tells: issuance, refinancing walls and private-credit redemptions, not the index." },
      { t: 'p', x: "The froth clears only when real enterprises' demand is actually paying and earning ROI — replacing recycled capital with real cash. It will accrue to whoever owns the enterprise control point: Microsoft's install base, not the commoditising model. Until then, capital markets simply reprice, day to day, whether the two ends of the chain connect before the levered builders run out of runway." }
    ],
    takeaways: [
      "Public equity stress is dispersion and a positioning unwind, not a bubble — the de-rating is already done.",
      "PE's exit machine is seized: DPI at 8–10% against a 15–20% norm, holding periods stretched to 7 years.",
      "Credit is the real transmitter: $500bn AI-related debt issuance expected in 2026, quality deteriorating and risk correlated across intermediary books.",
      "Liquidity is the master risk; real end-demand must replace recycled capital for the chain to hold."
    ]
  },

  'ai-marathon': {
    tag: 'AI Transformation',
    sectorKey: 'ai',
    date: 'Jun 2026',
    read: '6 min read',
    title: 'AI Transformation: A Marathon Race Needs Mental and Physical Preparation',
    dek: "The companies struggling most with AI adoption aren't the ones who moved too slowly — they're the ones who committed before they were ready.",
    body: [
      { t: 'lead', x: "A marathon runner doesn't show up on race day having only trained for a sprint. They've studied the course and built endurance over months to reach the goal. AI transformation demands the same discipline — not excitement about the destination, but honest preparation for what the journey actually costs." },
      { t: 'p', x: "The companies struggling most with AI adoption aren't the ones who moved too slowly. They're the ones who committed before they were ready. When Fortune 500 CEOs are gathered in rooms by institutional investors, they're asking a simple question: <strong>when does the AI investment actually pay back?</strong> If the world's largest companies are still working this out, SMEs rushing into AI transformation without a framework are taking on risk they haven't fully priced." },
      { t: 'h2', x: "Make sure you're stepping into the right story" },
      { t: 'p', x: "While the hyperscalers carry the AI hype, most companies sit beneath the success stories as followers trying hard to keep up. The AI leaders — Nvidia, Broadcom, Anthropic — are genuinely profitable and growing at extraordinary rates. The enterprise adopters are a different story. Even a name like Salesforce shows only 8–9% organic growth once acquisitions are stripped out." },
      { t: 'quote', x: "The productivity-to-profit conversion at the AI adopter layer is still unproven at scale." },
      { t: 'p', x: "SMEs should know which economy they're being invited into — the one building the picks and shovels, or the one still trying to prove the gold is there." },
      { t: 'h2', x: "Why are you lagging on AI transformation?" },
      { t: 'p', x: "When legacy systems, entrenched workflows, established habits and incompatible data architectures built over years meet AI implementation, it creates genuine friction. Workers have to change how they do things, learn new interfaces, trust outputs they can't fully verify, and integrate tools that don't usually speak to each other." },
      { t: 'p', x: "The drag is real and measurable — and it's the heart of the question everyone is asking: why aren't the productivity gains materialising, and why isn't it generating the revenue I expected?" },
      { t: 'h2', x: "The bottleneck is data infrastructure" },
      { t: 'p', x: "Enterprise AI requires your proprietary data to be clean, integrated and accessible. Most SMEs have their data scattered across incompatible legacy systems. Deploying AI before solving the data-architecture problem is building a race car without wheels. Three questions belong before any AI transformation:" },
      { t: 'list', x: [
        "<strong>What you want AI to know</strong> — define the proprietary insight the business needs, and the goal you need AI to help achieve.",
        "<strong>What must happen to the data first</strong> — cleansing, standardisation, integration, labelling, governance.",
        "<strong>Which AI tool</strong>, trained on what, deployed where, and measured how."
      ]},
      { t: 'h2', x: "Be selective" },
      { t: 'p', x: "Pricing power sits on the other side. GPU pricing is set by Nvidia. Cloud compute rates are set by the hyperscalers. The supply chain is concentrated among a handful of providers with extraordinary pricing power that will persist for the foreseeable future. Value-sensitive businesses should model their AI costs at current prices — not assume competition will drive them down soon." },
      { t: 'p', x: "Not all AI investment is equal. Core capabilities — the models, the memory, the compute — are where genuine value is being built. Peripheral AI adjacency, where everyone can package themselves as an 'AI company' with nice framing, is where the risk of overpaying for hype lives. SMEs should ask whether the tool they're adopting solves a genuine bottleneck in their operations, or merely creates demand that burns cash to chase a trend and avoid feeling left behind." },
      { t: 'h2', x: "Join the race with a clear goal" },
      { t: 'p', x: "For enterprises evaluating AI vendors, that has a practical implication: be cautious of vendors whose pitch is driven by what the market currently rewards rather than what your specific business actually needs. The coding-agent wave is real, but not every business needs coding agents — and vendors optimising their messaging for investor narratives rather than client outcomes are a warning sign." }
    ],
    takeaways: [
      "AI's profits today sit with the infrastructure leaders, not the enterprise adopters — know which economy you're entering.",
      "Fix data architecture before deploying AI; scattered legacy data is the real bottleneck.",
      "Model AI costs at today's prices — pricing power sits with Nvidia and the hyperscalers.",
      "Buy capability that solves a real bottleneck, not AI-adjacency sold on hype."
    ]
  },

  'london-ai-value-chain': {
    tag: 'EU Tech',
    sectorKey: 'eu',
    date: 'Jun 2026',
    read: '5 min read',
    title: 'Where Does London Actually Fit in the AI Value Chain?',
    dek: "The EU Tech Sovereign Package and London Tech Week are promising — but they promise too much.",
    body: [
      { t: 'lead', x: "The EU Tech Sovereign Package, arriving on 3 June, covers four pillars: a Cloud and Data Act (CADAA), Chips Act 2.0, open-source software promotion and AI data-centre investment — ideally to 'carve out a protected slice of the market before geopolitical disruption forces the issue.' Alongside it, London Tech Week is trying to position the UK as the European AI hub and find its place in the global AI value chain." },
      { t: 'p', x: "Both are positive political signals for AI development on a continent that has been left out of the dominant AI discourse for a while. They're promising — but they promise too much, creating funding black holes before the resource-allocation question is resolved." },
      { t: 'quote', x: "The value of this continent isn't capital itself, but the government credibility it confers." },
      { t: 'p', x: "Isomorphic Labs, an Alphabet unit, says the UK government stamp is genuinely meaningful for business development. The UK's strength in research, finance and regulatory agility — Waymo launching outside the US for the first time in the UK — are genuine assets that pure capital comparisons miss." },
      { t: 'h2', x: "London's natural position" },
      { t: 'p', x: "Imagine London as an enterprise accelerating AI adoption. The evidence points toward three positions: <strong>financial-services AI</strong>, <strong>life-sciences and drug-discovery AI</strong>, and <strong>regulatory and governance expertise</strong> — the one area where Europe genuinely leads the US." },
      { t: 'p', x: "These are London's natural positions in the AI value chain. Not infrastructure buildout competing with Texas data centres; not chip manufacturing competing with Asia. The energy-cost disadvantage — roughly 3× the US — makes infrastructure an even worse bet." },
      { t: 'h2', x: "The sovereign-data moat" },
      { t: 'p', x: "The concerns also point to the next move. The NHS holds one of the world's largest sovereign health datasets — a genuine moat no private company can replicate. Successfully integrating AI into that system would position London at the frontier of sovereign AI in healthcare, ahead of every market where the big players are still competing for data access they don't yet have." }
    ],
    takeaways: [
      "EU and UK AI policy signals are welcome but over-promise before resource allocation is settled.",
      "The UK's real edge is credibility, research, finance and regulatory agility — not capital scale.",
      "London should target financial-services AI, life sciences and governance — not infrastructure or chips.",
      "The NHS sovereign health dataset is a moat no private company can replicate."
    ]
  },

  'energy-beneath-ai': {
    tag: 'Energy',
    sectorKey: 'energy',
    date: 'Jun 2026',
    read: '6 min read',
    title: 'The Energy Beneath the AI Wave: Opportunity, Risk, and the Race for Infrastructure Control',
    dek: "Energy is not a peripheral theme in the AI buildout. It's the binding constraint that determines how fast the whole thing can scale.",
    body: [
      { t: 'lead', x: "The AI boom is driving growth across memory, semiconductors and energy. With $700bn of capex invested — expected to reach $800bn by the end of 2026 — large data-centre buildout is intensifying energy-supply constraints across the entire chain, making the energy transition a critical issue now." },
      { t: 'p', x: "Solar inverters, EV powertrains and grid-management systems have all seen rising demand in recent months, and that will only surge as hyperscalers keep burning huge cash flows on capex." },
      { t: 'h2', x: "The parallel story" },
      { t: 'p', x: "Another, equally significant story runs in parallel: war-driven energy inflation is compressing discretionary spending, deteriorating government fiscal positions, and pushing the K-shaped economy even wider. The greatest disruption to the global supply chain in history is escalating fears and lifting inflation — bond yields rising, stocks falling, indices moving together." },
      { t: 'p', x: "You might point to the all-time highs in the S&P 500 and Nasdaq, but the advance-decline line is slower than in February and April. More stocks are falling than rising, masked by the extraordinary performance of the top 30 companies — which now account for two-thirds of market cap." },
      { t: 'quote', x: "Whoever controls the energy-distribution layer of AI has a structural advantage that pure software companies cannot replicate." },
      { t: 'h2', x: "Where the opportunity emerges" },
      { t: 'p', x: "Opportunity emerges when energy catches the AI tailwind. An energy story can be framed as an AI story: compute requires power, power requires infrastructure, and whoever controls the energy-distribution layer holds a structural advantage that pure software companies cannot replicate." },
      { t: 'p', x: "Consider SpaceX's dominant control over its own energy distribution; the vertical integration of energy in sovereign AI as a service opportunity; even the emergence of CAT bonds financing data-centre energy risk, creating an entirely new insurance market around AI infrastructure." },
      { t: 'p', x: "Energy is not a peripheral theme in the AI buildout. It's the binding constraint that determines how fast the whole thing can actually scale — even as all eyes turn to the largest IPO in history." }
    ],
    takeaways: [
      "$700bn AI capex (heading to $800bn by end-2026) is tightening energy supply across the chain.",
      "Energy inflation is widening the K-shaped economy; market breadth is narrowing beneath record indices.",
      "Control of the energy-distribution layer is a structural advantage software can't replicate.",
      "New financing — e.g. CAT bonds on data-centre energy risk — is building an insurance market around AI infrastructure."
    ]
  }
};

/* ════════ SHARED HELPERS ════════ */

function articlesBySector(key) {
  return Object.keys(ARTICLES).filter(id => ARTICLES[id].sectorKey === key);
}

function articleCard(id, extraClass) {
  const a = ARTICLES[id];
  return `<a class="insight-card reveal ${extraClass || ''}" href="insight.html?id=${id}">
    <div class="ic-meta">
      <span class="ic-tag">${a.tag}</span>
      <span class="ic-date">${a.date}</span>
    </div>
    <h3>${a.title}</h3>
    <p>${a.dek}</p>
    <span class="ic-link">Read Brief</span>
  </a>`;
}
