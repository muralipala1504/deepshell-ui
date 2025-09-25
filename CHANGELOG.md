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
