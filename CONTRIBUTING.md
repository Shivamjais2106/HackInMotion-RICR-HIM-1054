# Contributing to KisanSathi

## Team Members
- Shivam Jaiswal
- Bhoomi Kesharwani
- Sumit Dangi
- Rustam Ali

## Git Workflow

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make changes with clear commit messages
3. Push and open a PR against `main`

## Commit Message Convention

```
type(scope): short description

Types: feat, fix, docs, chore, refactor, test, security
```

## Security Guidelines

- Never commit `.env` files — use `.env.example` as template
- All API keys must be loaded via `os.getenv()`
- Passwords must be hashed with bcrypt before storage
- Run `ruff check .` before committing Python code
- Run `npm run lint` before committing frontend code
