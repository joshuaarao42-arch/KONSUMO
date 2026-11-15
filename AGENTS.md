# Agent Instructions

## Neon / PostgreSQL

KONSUMO uses the existing Neon PostgreSQL project for hosted data and SQLite only for local development.

- Neon organization: `org-snowy-dawn-51105851`
- Neon project: `damp-tooth-64994055`
- Neon default branch: `production` (`br-odd-shadow-azftseca`)
- Neon region: `aws-ap-southeast-1` (Singapore)
- The Vercel project supplies `DATABASE_URL` as an encrypted environment variable. Never commit, print, log, or expose its value.
- Use the pooled Neon connection string for application traffic. Do not hardcode credentials in source, tests, documentation, or GitHub Actions.
- Preserve the existing database adapter and authentication implementation unless a requested change requires modifying them. Do not replace the current authentication system with Neon Auth without explicit direction.
- Before changing schema, inspect the current schema and migration approach. Prefer additive, repeatable migrations; do not drop or rewrite production data.
- Use a Neon development branch for schema experiments when available. Review the diff before applying changes to production.
- Verify real application flows (database health, signup, login, and account-scoped records), not just successful deployment or environment-variable setup.
- Treat Neon MCP operations as development/testing operations. Review every proposed write or destructive operation and obtain confirmation before destructive changes.
- Keep Neon skills and documentation current. Consult the installed Neon skills and official Neon documentation rather than guessing CLI commands or API behavior.

## Branch-first workflow

When a task changes database schema or data behavior:
1. Create or select a matching Git branch and a corresponding Neon development branch.
2. Implement and test against the development branch.
3. Inspect the schema diff and verify migration safety.
4. Merge code only after tests pass.
5. Apply production schema changes deliberately and verify the deployed application.

Do not create a new Neon project or rotate credentials as a workaround for application errors. Reuse the existing project and report authentication or permission failures clearly.
