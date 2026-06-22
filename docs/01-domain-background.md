# 01 — Domain Background: Cybersecurity

This document summarizes the cybersecurity concepts that frame our evaluation. Establishing this
background is important for two reasons: it defines the knowledge space the **Teacher** models are
expected to draw questions from, and it gives us the vocabulary needed to interpret whether
**Student** answers and **Judge** scores are technically sound.

---

## 1. The CIA Triad

The foundation of information security is the **CIA triad**, three properties every defensive
measure ultimately serves:

| Property | Meaning |
|----------|---------|
| **Confidentiality** | Information is accessible only to authorized parties. |
| **Integrity** | Information is not altered without authorization. |
| **Availability** | Information and services are accessible when needed. |

Every attack can be framed as a violation of one or more of these properties.

---

## 2. Attack categories

**Network attacks** — Denial of Service (DoS/DDoS), Man-in-the-Middle (MitM), port scanning, and
packet sniffing target the transport of data across networks.

**Web application attacks** — SQL Injection (SQLi), Cross-Site Scripting (XSS), Cross-Site Request
Forgery (CSRF), and Insecure Direct Object Reference (IDOR) exploit weaknesses in web software. The
**OWASP Top 10** is the canonical reference list of these risks.

**Malware** — viruses, ransomware, trojans, and rootkits are malicious programs differentiated by
how they propagate, hide, and inflict damage.

**Social engineering** — phishing, spear-phishing, and pretexting attack the human element rather
than the technical one.

---

## 3. Cryptography

| Mechanism | Property | Examples |
|-----------|----------|----------|
| **Symmetric encryption** | One shared key for encryption and decryption; fast, but key distribution is hard | AES, 3DES |
| **Asymmetric encryption** | Public/private key pair; enables HTTPS, digital signatures, SSH | RSA, ECC |
| **Hashing** | One-way fixed-length digest; password storage, integrity checks | SHA-256, bcrypt |
| **PKI** | Trust infrastructure based on certificates issued by Certificate Authorities | TLS/SSL |

---

## 4. Defensive mechanisms

Firewalls (network traffic filtering), IDS/IPS (intrusion detection/prevention), VPNs (encrypted
tunnels), MFA (multi-factor authentication), WAFs (web application firewalls), and SIEM (security
information and event management) form layered defenses. Two guiding principles recur:

- **Least Privilege** — every entity receives the minimum permissions necessary.
- **Defense in Depth** — multiple independent layers so one breach does not collapse the system.

---

## 5. Frameworks, standards, and reference data

- **OWASP Top 10** — most common web application risks.
- **MITRE ATT&CK** — knowledge base of real-world adversary techniques.
- **NIST Cybersecurity Framework** — risk-management structure.
- **CVE / CVSS** — catalog of known vulnerabilities and their severity scores (0–10).

---

## 6. Penetration testing

A structured simulation of a real attack, typically following the chain:

```
Reconnaissance → Scanning → Exploitation → Post-Exploitation → Reporting
```

Engagements are categorized as **Black Box** (no prior knowledge), **White Box** (full access), or
**Grey Box** (partial access — the most common in practice).

---

## 7. Additional key concepts

- **Zero-Day** — a vulnerability with no available patch.
- **APT (Advanced Persistent Threat)** — a prolonged, sophisticated, often state-sponsored attack.
- **Attack Surface** — the sum of all possible entry points into a system.

---

### Relevance to this study

These concepts collectively define the **target attribute space** that CoEval's Teacher models
infer automatically in Phase 1. In our runs the framework independently produced sub-topic
attributes closely matching this taxonomy (network security, web vulnerabilities, cryptography,
malware, defensive practice) — evidence that the automatic attribute mapping captured a sensible
structure of the domain. The auto-generated scoring rubric (Phase 2) likewise centered on
*technical accuracy*, *terminology*, *practical insight*, and *clarity* — the same qualities a
human cybersecurity expert would assess.
