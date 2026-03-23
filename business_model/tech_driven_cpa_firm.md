# Business Model: Tech-Driven CPA Firm — Quebec SME Market

**Target Market:** Quebec small and medium enterprises (SMEs), with initial focus on
Montreal hospitality sector (restaurants, bars, hotels, catering).

---

## 1. Executive Summary

A **cloud-first, automation-heavy CPA firm** that replaces the traditional
time-and-billing model with **fixed-fee advisory packages**. By standardizing the
tech stack (cloud accounting, automated document capture, integrated payroll, and
AI-assisted tax preparation), the firm achieves higher margins through operational
leverage while delivering superior client outcomes.

**Core thesis:** Most Quebec SME accounting is repetitive compliance work that can
be 70–80% automated. The freed-up capacity is redirected to advisory services that
command higher fees and generate stickier client relationships.

---

## 2. Market Opportunity

### Quebec SME Landscape

| Metric | Value |
|--------|-------|
| Number of SMEs in Quebec | ~265,000 (with employees) |
| Quebec restaurant establishments | ~22,000 |
| Average SME accounting spend | $5,000–$25,000/year |
| Total addressable market (TAM) — QC SME accounting | ~$3B+ |
| Serviceable addressable market (restaurants, hospitality) | ~$400M |
| SRM/MEV-mandatory establishments | ~40,000 |

### Pain Points Solved

1. **Compliance complexity** — Dual CRA + Revenu Québec filings, SRM/MEV, tip reporting
2. **Bilingual requirements** — Firms must operate in French (Loi 101) with English capability
3. **Fragmented tech stacks** — Most SMEs use disconnected, outdated software
4. **Reactive accounting** — Traditional firms deliver year-end surprises, not real-time insight
5. **Talent shortage** — Quebec CPA pipeline cannot meet demand; automation is the multiplier

### Competitive Advantages in Quebec

- **SRM/MEV expertise** — Deep specialization most generalist firms lack
- **PME-6.1 optimization** — Proactive tip credit maximization (many firms miss this entirely)
- **Bilingual-first** — All systems, communications, and deliverables in French and English
- **Quebec payroll mastery** — QPP2, QPIP, CNESST, HSF — provincial complexity as a moat
- **Revenu Québec relationship** — Understanding of RQ audit patterns and compliance culture

---

## 3. Service Tiers & Pricing

### Tier 1: Conformité (Compliance) — $500–$1,500/month

**Target:** Solo-operated or family restaurants, revenues < $1M

| Service | Frequency |
|---------|-----------|
| Cloud accounting setup and maintenance (QBO/Sage) | Ongoing |
| Dext document capture and expense coding | Ongoing |
| Monthly bank reconciliation | Monthly |
| SRM/MEV-to-GL reconciliation | Monthly |
| GST/QST return preparation and filing | Quarterly |
| Payroll processing (up to 10 employees) | Semi-monthly |
| T4/RL-1 slip preparation | Annual |
| T2 + CO-17 preparation and filing | Annual |
| PME-6.1 tip credit claim | Annual |

**Unit economics:**
- Average monthly fee: $800
- Estimated labour hours per client per month: 4–6
- Target: 80% automated, 20% manual review
- Gross margin target: 65–70%

### Tier 2: Croissance (Growth Advisory) — $1,500–$3,500/month

**Target:** Multi-unit or high-revenue restaurants, revenues $1M–$5M

Everything in Tier 1, plus:

| Service | Frequency |
|---------|-----------|
| Monthly financial statements with KPI dashboard | Monthly |
| Food cost and labour cost analysis | Monthly |
| Cash flow forecasting | Monthly |
| Tax instalment optimization | Quarterly |
| CCA/amortization planning for capital investments | As needed |
| Shareholder remuneration optimization (salary vs. dividend) | Annual |
| CNESST experience rating management | Annual |
| Budget vs. actual variance analysis | Monthly |
| Quarterly strategic review call with CPA | Quarterly |

**Unit economics:**
- Average monthly fee: $2,200
- Estimated labour hours per client per month: 8–12
- Target: 60% automated, 40% advisory
- Gross margin target: 60–65%

### Tier 3: Stratégie (CFO Services) — $3,500–$8,000/month

**Target:** Restaurant groups, multi-location hospitality, revenues $5M+

Everything in Tier 2, plus:

| Service | Frequency |
|---------|-----------|
| Fractional CFO services (dedicated senior CPA) | Ongoing |
| Multi-entity consolidation | Monthly |
| Intercompany transaction management | Ongoing |
| Financing support (bank presentations, loan covenants) | As needed |
| M&A due diligence (acquisition of additional locations) | As needed |
| SR&ED credit identification (food tech innovation) | Annual |
| Succession and estate planning coordination | Annual |
| Custom reporting and BI dashboard | Ongoing |
| Revenu Québec / CRA audit representation | As needed |

**Unit economics:**
- Average monthly fee: $5,500
- Estimated labour hours per client per month: 15–25
- Target: 40% automated, 60% advisory
- Gross margin target: 55–60%

---

## 4. Technology Platform Architecture

### Client-Facing Stack

```
┌──────────────────────────────────────────────┐
│            CLIENT PORTAL (Custom)              │
│  ┌─────────┐ ┌──────────┐ ┌───────────────┐  │
│  │Dashboard │ │Documents │ │ Messages/Chat │  │
│  │  (KPIs)  │ │ (Upload) │ │  (Async CPA)  │  │
│  └─────────┘ └──────────┘ └───────────────┘  │
└──────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────────────────────────────────────┐
│          INTEGRATION LAYER (Make/Zapier)       │
│  ┌───────┐ ┌──────┐ ┌────────┐ ┌──────────┐ │
│  │  QBO  │ │ Dext │ │Payroll │ │ TaxCycle │ │
│  └───────┘ └──────┘ └────────┘ └──────────┘ │
└──────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────────────────────────────────────┐
│         INTERNAL WORKFLOW ENGINE               │
│  ┌──────────┐ ┌────────────┐ ┌────────────┐ │
│  │Task Mgmt │ │  QC Review │ │  Deadline  │ │
│  │(Karbon)  │ │  Checklists│ │  Tracking  │ │
│  └──────────┘ └────────────┘ └────────────┘ │
└──────────────────────────────────────────────┘
```

### Internal Operations Stack

| Function | Tool | Purpose |
|----------|------|---------|
| Practice management | Karbon or Canopy | Workflow, task management, client communication |
| Document management | SharePoint or Google Workspace | Secure document storage, collaboration |
| Tax preparation | TaxCycle | T2, CO-17, GST/QST, T4/RL-1 |
| Time tracking | Built into Karbon | Internal capacity planning (not client billing) |
| Client portal | Custom or Canopy | Dashboard, document exchange, messaging |
| KPI dashboards | Fathom or Jirav | Client-facing financial analytics |
| Internal AI/Automation | Custom scripts + Make | Data extraction, reconciliation automation |

---

## 5. Operational Model

### Team Structure (at Scale — 200 Clients)

| Role | FTE | Ratio | Responsibilities |
|------|-----|-------|------------------|
| Managing Partner (CPA) | 1 | 1:200 | Strategy, key client relationships, BD |
| Senior CPAs (5+ yrs) | 2 | 1:100 | Review, advisory, complex filings |
| Staff CPAs (1–5 yrs) | 3 | 1:67 | Preparation, client communication |
| Bookkeeping Technicians | 4 | 1:50 | Monthly accounting, Dext management |
| Payroll Specialist | 1 | 1:200 | Payroll processing, RL-1/T4 |
| Technology / Automation Lead | 1 | 1:200 | Integrations, workflow optimization |
| Client Success / Onboarding | 1 | 1:200 | Onboarding, training, retention |
| **Total** | **13** | | |

**Key metric:** Revenue per employee target: $150,000–$200,000
(vs. traditional firm: $80,000–$120,000)

### Client Onboarding Workflow (Standardized — 2 Week Target)

| Day | Action |
|-----|--------|
| 1–2 | Discovery call, engagement letter, KYC/AML |
| 3–4 | QBO setup (or migration from existing software) |
| 5–6 | Dext setup, supplier rule configuration |
| 7–8 | Payroll system setup, employee onboarding |
| 9–10 | POS/SRM integration, bank feed connection |
| 11–12 | Historical data migration (current FY minimum) |
| 13–14 | Client training, portal walkthrough, go-live |

### Quality Control Framework

- **Three-tier review:** Technician → Staff CPA → Senior CPA
- **Automated checklists:** Embedded in Karbon for every deliverable
- **SRM reconciliation:** Monthly sign-off required before period close
- **Tax return review:** Mandatory senior review before e-filing
- **Continuous monitoring:** Automated alerts for anomalies (see workflow_config.yaml)

---

## 6. Revenue Model & Financial Projections

### Revenue Mix Target (Year 3)

| Source | % of Revenue | Description |
|--------|-------------|-------------|
| Tier 1 (Conformité) | 35% | High volume, high automation |
| Tier 2 (Croissance) | 40% | Core growth segment |
| Tier 3 (Stratégie) | 15% | High-value, relationship-intensive |
| Project / Advisory fees | 10% | One-time projects (restructuring, M&A, audit defence) |

### Illustrative P&L (Year 3 — 200 Clients)

| Line Item | Annual |
|-----------|--------|
| **Revenue** | |
| Tier 1 (100 clients × $800/mo × 12) | $960,000 |
| Tier 2 (70 clients × $2,200/mo × 12) | $1,848,000 |
| Tier 3 (20 clients × $5,500/mo × 12) | $1,320,000 |
| Project fees (10 clients × $8,000 avg) | $80,000 |
| **Total Revenue** | **$4,208,000** |
| | |
| **Expenses** | |
| Salaries and benefits (13 FTE) | $1,680,000 |
| Software and technology | $180,000 |
| Office / co-working space | $120,000 |
| Insurance (E&O, cyber, general) | $60,000 |
| Marketing and business development | $150,000 |
| Professional development / CPD | $40,000 |
| Other operating expenses | $100,000 |
| **Total Expenses** | **$2,330,000** |
| | |
| **EBITDA** | **$1,878,000** |
| **EBITDA Margin** | **44.6%** |

### Key Performance Indicators

| KPI | Target |
|-----|--------|
| Monthly recurring revenue (MRR) | $350K+ (Year 3) |
| Client retention rate | > 95% |
| Revenue per FTE | $175K+ |
| Client acquisition cost (CAC) | < $2,000 |
| Client lifetime value (LTV) | > $60,000 |
| LTV:CAC ratio | > 30:1 |
| NPS (Net Promoter Score) | > 60 |
| Average onboarding time | < 14 days |
| Automation rate (compliance work) | > 70% |

---

## 7. Go-to-Market Strategy

### Phase 1: Beachhead (Months 1–12) — 50 Clients

**Focus:** Montreal restaurants — leverage SRM/MEV and PME-6.1 expertise

- Partner with Lightspeed (Montreal-based POS) for co-marketing
- Sponsor and present at ARRQ (Association des restaurateurs du Québec) events
- Content marketing: "Guide SRM/MEV pour restaurateurs" (French-first)
- Referral network: immigration lawyers (new restaurant owners), commercial realtors
- Google Ads targeting: "comptable restaurant Montréal," "CPA restaurant Québec"
- Social proof: case studies showing PME-6.1 credit savings (e.g., Giwa's ~$29K credit)

### Phase 2: Expand Hospitality (Months 12–24) — 120 Clients

**Focus:** Hotels, bars, catering companies, food trucks

- Expand to Quebec City and Gatineau markets
- Partner with CQRHT (Conseil québécois des ressources humaines en tourisme)
- Add hotel-specific modules (tourism levy, accommodation tax)
- Develop referral partnerships with 3–5 complementary firms (legal, insurance)

### Phase 3: Broader Quebec SME (Months 24–36) — 200 Clients

**Focus:** Retail, professional services, construction — any SRM-adjacent or payroll-heavy SME

- Develop industry-specific compliance packages
- Explore white-label bookkeeping partnerships
- Consider acquisition of 1–2 small traditional firms for client book
- Build proprietary automation tooling for competitive moat

---

## 8. Regulatory & Professional Considerations

### CPA Quebec (Ordre des CPA du Québec)

- [ ] All client-facing professionals must hold valid CPA designation
- [ ] Firm must be registered with the Ordre des CPA du Québec
- [ ] Comply with CPA Quebec practice inspection requirements
- [ ] Maintain professional liability insurance (E&O)
- [ ] Annual CPD requirements: 40 hours per CPA

### Loi 101 (Charter of the French Language)

- [ ] All client communications available in French
- [ ] Software interfaces must support French
- [ ] Marketing materials primarily in French
- [ ] Employment contracts and internal documents in French

### Privacy (Law 25 — Quebec's Privacy Law)

- [ ] Privacy impact assessment for client data handling
- [ ] Designated privacy officer
- [ ] Client consent for data processing and cloud storage
- [ ] Incident response plan for data breaches
- [ ] Vendor agreements with cloud providers (data residency in Canada)

### Anti-Money Laundering (AML)

- [ ] CPA firms are reporting entities under PCMLTFA
- [ ] KYC procedures for all new clients
- [ ] Suspicious transaction reporting obligations
- [ ] Record keeping per FINTRAC requirements

---

## 9. Competitive Differentiation Summary

| Traditional Firm | This Firm |
|---|---|
| Hourly billing — unpredictable costs | Fixed monthly fees — budget certainty |
| Year-end-only engagement | Real-time cloud accounting + monthly close |
| Paper-based, manual processes | Automated capture, reconciliation, filing |
| Generic SME service | Hospitality-specialized (SRM/MEV, tips, CNESST) |
| Reactive compliance | Proactive advisory + compliance |
| English-first with French capability | French-first with full bilingual capability |
| Desktop software (Sage 50, Profile) | Cloud-native (QBO, Dext, TaxCycle) |
| One CPA does everything | Specialized team with defined workflows |
| No client portal | Real-time dashboard with KPIs and document exchange |
| Miss credits like PME-6.1 | Systematic credit optimization — never miss a dollar |

---

## 10. Risk Factors & Mitigation

| Risk | Mitigation |
|------|------------|
| Client concentration in hospitality | Diversify to other SME sectors by Phase 3 |
| Software vendor dependency (QBO, Dext) | Maintain migration playbooks for alternatives |
| Talent retention (CPAs in demand) | Competitive comp + equity/profit sharing + modern culture |
| Regulatory change (SRM/MEV rules evolve) | Dedicated regulatory monitoring + RQ relationship |
| Cybersecurity / data breach | SOC 2 Type II controls, cyber insurance, Canadian data residency |
| Economic downturn affecting restaurants | Advisory services become more valuable in downturns |
| AI disruption of compliance work | Embrace AI — automate compliance, double down on advisory |

---

*This business model is a strategic framework. Financial projections are illustrative
and should be validated with market-specific data. Consult with a business advisor
and the Ordre des CPA du Québec before establishing a practice.*
