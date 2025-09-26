
## [1.2.0] - 2025-09-26
### Added
- Hardened domain filtering in `wrapper.py` with stricter default‑deny behavior.
- Context-aware blocks for playful/non-infra prompts (e.g., “tree”, “coffee”, “startup pitch”, “favorite”, “fluffy”).
- Trivia/question-word filter: blocks general Q&A starting with “who/what/when/where/why/how many” unless tied to actionable infra tasks.
- Expanded test coverage via `prompt_tests.md` for 18 sneaky cases across 6 categories.

### Changed
- Expanded `EXCLUDED_CONTEXT` and refined `ALLOWED_KEYWORDS` to better separate infra tasks from non-infra chatter.
- More consistent refusals for finance/business/crypto related prompts mixed with CI/CD terms.

### Fixed
- Leaks where prompts mixed valid infra keywords with non-infra context:
  - “Terraform script that grows a tree” (blocked)
  - “Docker command to start my day with coffee” (blocked)
  - “Jenkins job to predict Bitcoin price” and “CI/CD for stock trading app” (blocked)
  - Trivia like “When was Kubernetes founded?” and “Who invented Terraform?” (blocked)

### Notes
- Deepshell-UI is now strictly infra-only: Linux, DevOps, Cloud, IaC. 
- Screenshots validating rejections are encouraged for README/docs.

## [v1.0.0] - 2025-09-19
### Added
- 🎉 First stable **public release** of Deepshell UI.
- Chat-style interface for interacting with the Deepshell backend (`/run-agent` endpoint).
- Syntax highlighting using Prism.js with an **always-visible copy button**.
- Compact & scrollable chat output layout for long responses.
- Navbar branding ("💻 Deepshell Chat UI").
- Updated `README.md` with badges, tech stack, and screenshot preview.
- Added project screenshot under `docs/screenshot.png`.

## [1.1.0] - 2025-09-25
### Added
- Domain filtering in backend (`wrapper.py`) to keep Deepshell-UI focused on Linux, DevOps, Cloud, and IaC.
- Smart handling for Chef/Puppet queries (infra-focused only, avoids food-related confusion).
- Automatic code-fence wrapping for outputs to ensure copy button is available.

### Changed
- Output cleaned: removed unnecessary prose, only copy-ready commands/scripts will be returned.

### Fixed
- Copy button missing issue on single-line commands (e.g. `docker ps -a`).
- Multi-line script formatting for Terraform/Ansible now displays correctly with copy support.

### Removed
- 🗑️ Deprecated `archive/` folder (old Docker/mkdocs files), now available in the `legacy-archive` branch for reference.
