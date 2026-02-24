# Security Policy 🛡️

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, email the maintainer directly (see the GitHub profile) or use GitHub's
[Private Vulnerability Reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability).

You should expect an acknowledgement within 48 hours.

## Handling of Credentials

- **Never commit secrets** to the repository.  The `.env` file is in `.gitignore`.
- Use `.env.example` as the template; it contains only placeholder values.
- `GITHUB_TOKEN` is read from the environment at runtime and never logged.

## Dependency Security

- Dependencies are kept minimal (see `requirements.txt`).
- Run `pip audit` periodically to check for known vulnerabilities.
