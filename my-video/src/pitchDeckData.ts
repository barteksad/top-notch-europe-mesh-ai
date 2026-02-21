export type PitchSlide = {
  readonly title: string;
  readonly bullets: readonly string[];
};

export const PITCH_SLIDES: readonly PitchSlide[] = [
  {
    "title": "SOCIAL.md",
    "bullets": [
      "Every product deserves a launch. We all have been there. Great idea, all night of hacking, and then what - project goes to trash! SOCIAL.md is an open protocol that gives every project a structured, agent-readable launch plan so your side-project, library, or startup gets the distribution it deserves.",
      "Stage: pre-seed",
      "Website: https://v0-social-md-website.vercel.app/",
      "Target raise: $750,000"
    ]
  },
  {
    "title": "Team",
    "bullets": [
      "Founder-led builders with direct pain insight from hackathon-to-distribution workflows.",
      "Shipped end-to-end narrative quickly: live launch page, protocol framing, and implementation-ready examples.",
      "Strong technical execution signal: automation skills and scripts for launch operations exist in this repository.",
      "Community-first orientation matches open protocol adoption dynamics for developer ecosystems."
    ]
  },
  {
    "title": "Problem",
    "bullets": [
      "Great products still fail because launch distribution is ad hoc and repeatability is missing.",
      "Builders spend energy shipping product, then run out of time to market while launch windows expire.",
      "Current workflow is usually one-off posting with no channel plan, no audience map, and no checklist.",
      "Each project relaunches from zero, so there is no compounding launch knowledge across projects.",
      "Agents cannot help effectively when launch context is unstructured."
    ]
  },
  {
    "title": "Solution",
    "bullets": [
      "SOCIAL.md standardizes launch context so humans and agents can execute distribution reliably.",
      "Add one SOCIAL.md file in repo root with project metadata, audiences, channels, assets, and tasks.",
      "Agents and automation tooling parse the same file to draft posts, generate assets, and track execution.",
      "Reusable templates turn launch from improvisation into repeatable operating workflow.",
      "Open protocol approach enables broad ecosystem integrations without platform lock-in."
    ]
  },
  {
    "title": "Why Now",
    "bullets": [
      "Agent-native workflows are mainstream enough that a launch protocol can become default infrastructure.",
      "AI agents are now part of developer workflows, making machine-readable launch context immediately useful.",
      "Distribution channels are fragmented; teams need one canonical source of launch truth.",
      "Open-source and indie product creation velocity keeps increasing, amplifying post-build distribution pain.",
      "A protocol-first standard can create network effects as templates and integrations compound."
    ]
  },
  {
    "title": "Traction",
    "bullets": [
      "Early proof is execution speed and concrete protocol articulation, with user validation as the next milestone.",
      "Live launch page already communicates end-user pain, protocol spec, examples, and contribution path.",
      "Product positioning is clear across three initial segments: hackathon projects, OSS libraries, and student startups.",
      "Core tooling exists to support downstream launch workflow elements (pitch creation and social automation).",
      "Immediate next step: convert current interest into design partners and measurable launch outcomes."
    ]
  },
  {
    "title": "Market",
    "bullets": [
      "Start with underserved builder segments, then expand into broader launch operations infrastructure.",
      "Beachhead: hackathon builders, OSS maintainers, and student founders who lack formal GTM support.",
      "Expansion: indie SaaS teams, developer tools startups, accelerators, and product education programs.",
      "Monetization path: hosted automation workflows, premium templates, team collaboration, and analytics/reporting.",
      "Protocol strategy can create defensibility through ecosystem standardization and workflow lock-in."
    ]
  },
  {
    "title": "Ask",
    "bullets": [
      "Raise amount: $750,000",
      "Runway target: 18 months",
      "Raise to validate repeatable user outcomes and ship protocol + automation v1.",
      "Use capital to move from narrative traction to measurable launch outcomes.",
      "Prioritize protocol quality, onboarding velocity, and design-partner conversion.",
      "Prepare a strong seed narrative based on validated activation and retention signals."
    ]
  }
] as const;
