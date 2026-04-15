# envault

> A CLI tool for securely managing and syncing `.env` files across team environments using encrypted vaults.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install envault
```

---

## Usage

**Initialize a new vault in your project:**
```bash
envault init
```

**Push your local `.env` to the vault:**
```bash
envault push --env .env
```

**Pull the latest secrets to your local environment:**
```bash
envault pull --env .env
```

**Manage team access:**
```bash
envault invite teammate@example.com
envault revoke teammate@example.com
```

Secrets are encrypted client-side before being stored. Only team members with authorized keys can decrypt vault contents.

---

## How It Works

1. `envault init` generates a vault config and a local encryption key
2. Secrets are encrypted using AES-256 before leaving your machine
3. Encrypted blobs are synced to a shared backend (local, S3, or envault cloud)
4. Team members pull and decrypt using their authorized key

---

## Requirements

- Python 3.8+
- An initialized vault (`envault init`)

---

## License

MIT © [envault contributors](LICENSE)