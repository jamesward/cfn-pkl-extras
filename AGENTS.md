# cfn-pkl-extras

Pkl package (`package://pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras@<version>`) of higher-level AWS CloudFormation abstractions (static sites, Route 53 domains and records, custom resources backed by the published jamesward/cfn-extras-resource artifact). Built with the `org.pkl-lang` Gradle plugin; released by pushing a `cfn-pkl-extras@X.Y.Z` tag (see DEV.md).

Follow the `zen-of-projects` Skill (extract it with `./gradlew extractSkillsJars`); this file records
only project-specific facts and exceptions.

## Skills

`zen-of-projects`, `zen-of-james` (from `com.jamesward:skills`, extracted to the gitignored `.kiro/skills/`).

## MCP

`javadocs` (https://www.javadocs.dev/mcp), configured in `.mcp.json` / `.kiro/settings/mcp.json` and
approved in `.claude/settings.json`. Use its `get_latest_version` for version lookups and its
source/doc tools for API questions. In Claude Code its tools are deferred: load them with ToolSearch
(search `javadocs`).

## Build & test

- Full validation: `./gradlew makePackages`.

## Maintenance routine

`.factory/MAINTENANCE.md` (weekly), following the `zen-of-projects` Skill.

## Exceptions to zen-of-projects

- **Workflows are generated from Pkl:** edit `.github/workflows/*.pkl`, then regenerate the YAML with `pkl eval -f yaml -o <name>.yaml <name>.pkl` (in `.github/workflows/`). Never edit the generated YAML by hand.
- **Releases:** never tag or release in the maintenance routine. Dependents such as jamesward/domains pin released versions.
- **cfn-extras-resource artifact:** `artifactObjectVersion` in `src/customResources.pkl` pins a published release of jamesward/cfn-extras-resource. Update it only to a version listed in `s3://cfn-extras-resource/versions/<tag>.json`.
