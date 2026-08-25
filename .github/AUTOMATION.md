# Automation

- `validate.yml` checks the framework on Linux, Windows, and macOS, tests the
  supported Python versions, installs the built wheel outside the repository,
  and verifies the paper-result mapping.
- `publish.yml` builds the wheel and source distribution, publishes an English
  release to PyPI through Trusted Publishing, and tests the public package.
- `fiqa260-smoke.yml` reconstructs a small FiQA-Compression260 route sample on
  CPU and checks the resulting ledger.

Simplified Chinese source tags are archival source releases and do not publish
a second package to PyPI.
