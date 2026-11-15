# Model costs: condensed research notes

Checked November 14, 2026. Read-only pitch_researcher verified the original official documentation; no inference API requests, credentials or production telemetry were used. Standard USD per one million tokens; taxes/discounts excluded.

## Verified rates and billing limits

[OpenAI pricing](https://developers.openai.com/api/docs/pricing.md) lists gpt-6.1-sol at US$2 input/US$10 output/US$0.10 cached input, and gpt-6-astra at US$10/US$50/US$1. [gpt-6.1-terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra.md) is US$1/US$5/US$0.05. Above 272K prompt input tokens per request, Standard input/cache rates double and output rates multiply by1.5. A cumulative million spread across shorter requests does not itself cross that threshold. Fast, Batch/Flex, cache-write retention and paid hosted tools have separate rate rules. This model assumes uncached Standard requests below the long-context threshold, no paid hosted tools and no discounts.

[OpenAI reasoning](https://developers.openai.com/api/docs/guides/reasoning) bills reasoning as output; an incomplete response can consume budget before useful visible text. Count every drafting/review/repair attempt, not just accepted hardware results.

[Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing) lists Sonnet5.5 US$2 input/US$10 output/US$0.10 cache hits and Opus5.5 US$4/US$20/US$0.20. Cache writes and some server tools cost separately. Equal footprints are not equal model capability.

[Groq GPT-OSS120b](https://console.groq.com/docs/model/openai/gpt-oss-120b) lists US$0.15 input/US$0.60 output/US$0.075 cached, 131,072 context and65,536 max output. [Caching](https://console.groq.com/docs/prompt-caching) depends on exact reusable prefixes; do not assume hits. The old Llama3.3 price is not used.

## Explicit unmeasured footprints

Template attempt: four calls totaling50,000 input and10,000 output tokens. Integration attempt:20 calls totaling1,000,000 input and200,000 output, including eight repair calls. Stress attempt:100 calls totaling10,000,000 input and2,000,000 output, including60 repair calls. Outputs include reasoning. These are illustrative cumulative workloads, not observed averages or success guarantees.

Cost is input/1M times input rate plus output/1M times output rate. Template/integration/stress costs respectively: Terra US$0.10/2/20; Sol US$0.20/4/40; Astra US$1/20/200; Sonnet5.5 US$0.20/4/40; Opus5.5 US$0.40/8/80; Groq OSS120b US$0.0135/0.27/2.70. Different repair/success rates can reverse an equal-token comparison.

One proposed internal AI-cost unit equals US$0.10 of provider-rated model/paid-tool spend; this is not a provider credit, retail price or Codex balance conversion. Failed engineering attempts can still cost tokens. Stop honestly at cost/token/retry/time limits; never weaken verification to stay within budget. No model token charge arises per sensor sample or FPGA clock. Local builds incur API charges only when model calls consume their inputs/logs.
