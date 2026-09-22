# Assisted Classification Methodology

## Purpose

The classification component demonstrates how structured automation could help
a risk professional triage a new issue description consistently. It is a
transparent rule-based prototype and does not use a large language model or a
paid external API.

## Outputs

The prototype suggests:

- primary risk category;
- root-cause category;
- risk theme;
- investigation areas; and
- the terms that triggered the suggestion.

## Method

The entered description is normalised and checked against documented business
term sets. The classification with the greatest number of direct matches is
returned. Match strength describes the amount of rule support; it is not a
statistical probability or assurance conclusion.

## Human-review controls

- Suggested classifications do not update the issue register automatically.
- Closure, escalation and regulatory conclusions remain human decisions.
- Matched terms are exposed so the reviewer can challenge the suggestion.
- Descriptions with limited evidence are labelled as limited rule matches or as
  requiring further assessment.

## Future development

A production design could compare the transparent baseline with an approved
language model, add a controlled taxonomy service, retain reviewer overrides,
monitor classification drift and test outcomes against a labelled validation
set.
