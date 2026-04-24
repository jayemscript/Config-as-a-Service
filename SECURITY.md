# Security Policy

## ⚠️ Important: MVP Status

**Config-as-a-Service is currently in ALPHA (v0.1.0) status.** This means:

- It is **NOT recommended for production use** at this time
- Security hardening is ongoing
- API may change without notice
- Use only on **trusted, internal networks** behind a firewall
- Do **NOT expose the API to the internet** without additional security layers

---

## Encryption Details

### Configuration Values Encryption

All sensitive configuration values are encrypted using **Fernet (symmetric encryption)** from the `cryptography` library:

- **Algorithm:** AES-128 in CBC mode with PKCS7 padding
- **Authenticity:** HMAC for tamper detection
- **Key Management:** 32-byte (256-bit) base64-encoded keys
- **Storage:** Encrypted values stored in SQLite database

### Best Practices for Encryption Keys

1. **Generate a Strong Key:**

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. **Store Securely:**
   - Use `.env` file (excluded from git)
   - Use environment variables
   - Never commit keys to version control

3. **Rotate Keys Periodically:**
   - Currently requires manual re-encryption of existing data
   - Future versions will support key rotation

---

## JWT Authentication

### Token Details

- **Algorithm:** HS256 (HMAC with SHA-256)
- **Expiration:** Configurable (default 24 hours)
- **Storage (CLI):** Local file at `~/.caas/token` with restrictive permissions (0600)

### Best Practices for JWT Secrets

1. **Generate a Strong Secret:**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Environment Variables:**
   - Set `JWT_SECRET_KEY` in `.env`
   - Use different secrets for different environments
   - Never hardcode secrets

3. **Token Management:**
   - Regenerate tokens via `caas auth generate-token`
   - Remove old tokens with `caas auth logout`

---

## Network Security

### Current Limitations

- **No HTTPS/TLS:** API runs on plain HTTP
- **No Rate Limiting:** Vulnerable to brute force attacks
- **No Request Signing:** Only JWT-based auth
- **Default Localhost:** Binds to `127.0.0.1` by default

### Recommendations

1. **Use Behind a Reverse Proxy:**
   - Deploy with nginx or Caddy
   - Enable HTTPS/TLS termination
   - Implement rate limiting
   - Use authentication layer (basic auth, OAuth2)

2. **Network Isolation:**
   - Run on internal networks only
   - Use firewall rules to restrict access
   - Whitelist trusted client IPs

3. **Access Control:**
   - Currently uses simple JWT tokens
   - Future versions will support API key rotation, scopes, and audit logging

---

## Database Security

### SQLite Considerations

- **File-Based:** Database is a local SQLite file
- **No Built-in Encryption:** SQLite database file itself is not encrypted
- **Access Control:** Rely on file system permissions

### Hardening Steps

1. **Restrict Database File Permissions:**

   ```bash
   chmod 600 caas_data.db
   ```

2. **Backup Securely:**
   - Encrypt backups at rest
   - Use secure transfer protocols
   - Limit access to backup files

3. **Future Enhancement:**
   - Consider SQLCipher for encrypted SQLite databases
   - Support for PostgreSQL/other databases

---

## Dependency Security

- **Minimal Dependencies:** FastAPI, SQLAlchemy, cryptography, PyJWT
- **Regular Updates:** Check for security patches monthly
- **Vulnerability Scanning:** Use `pip-audit` or similar tools

```bash
# Check for known vulnerabilities
pip-audit
```

---

## Reporting Security Issues

⚠️ **Do NOT open public issues for security vulnerabilities.**

If you discover a security issue:

1. Email: [Create a reporting contact if applicable]
2. Do not disclose publicly until a patch is available
3. Allow 30 days for response and patch release
4. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## Future Security Roadmap

- [ ] HTTPS/TLS support
- [ ] Rate limiting
- [ ] Request signing and verification
- [ ] Audit logging
- [ ] Support for encrypted SQLite (SQLCipher)
- [ ] API key rotation and scoping
- [ ] CORS policy refinement
- [ ] Input validation hardening
- [ ] DDoS protection recommendations

---

## Security Headers (Future)

When deployed behind a reverse proxy, ensure these headers are set:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## Compliance & Standards

This project aims to follow security best practices from:

- OWASP Top 10
- CWE Top 25
- Python security guidelines (PEP 644)

However, **do not use in compliance-critical environments** (HIPAA, PCI-DSS, etc.) without additional hardening.

---

## Questions?

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get involved or ask questions safely.
