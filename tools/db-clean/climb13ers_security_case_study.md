# Climb13ers — Security Incident & Stabilization (Case Study for Mastermind Group)

**Scope:** This case study is compiled *only* from the Climb13ers project and focuses on cybersecurity and the malicious-file cleanse, plus the brownouts observed on the old hosting platform.

---

## 1) Situation Overview (What I inherited)
- **Hosting:** Legacy site on Arcustech (pre-migration), Craft CMS (legacy version) with a Vae-era legacy code throughout.
- **State of codebase:** No `node_modules`; no frontend platform used.
- **Operational pain:** Intermittent **brownouts** (temporary crashes/unresponsiveness), especially during peak season.
- **Security posture at intake:** Indicators of previous compromise/hardening gaps: need to scrub sessions/tokens, refresh dependencies, and add request filtering in `.htaccess`.

> Notes: vendor refresh to eliminate potential malicious code; database/session scrub; `.htaccess` hardening work; and detailed explanation of brownouts being driven by a heavy-template + cold-cache pattern compounded by bot traffic on an outdated stack.

---

## 2) Initial Compromise (Before the involvement)
- Evidence points to a prior compromise or, at minimum, a **high-risk environment**:
  - **`vendor/` distrust**: I treated the existing `vendor/` directory as untrusted and rebuilt from lockfile.
  - **Database hygiene issues**: Required clearing sessions/tokens/queues, which are often abused post-compromise.
  - **Outdated CMS/plugins**: Older Craft versions increase the attack surface and contribute to instability under load.
   - **Technical Debt**: The presence of old **Vae-style files** were discovered which complicated the transition process to **Docker & Servd hosting**.
- I pulled down **zipped assets** and a project snapshot to analyze; there were **no custom plugins** in play (reduced surface), but legacy routing and older code paths remained.

> Takeaway: Even without a confirmed list of injected files, the combination of an untrusted `vendor/`, stale sessions, and old CMS is consistent with environments that have been probed or compromised.

---

## 3) Investigation & Containment (What I did first)
1. **Dependency Reset**
   - Deleted `vendor/` entirely in order to remove any possible injected malicious files.
   - Reinstalled dependencies from `composer.lock` to ensure a pristine, verified codebase.
2. **Database Scrub**
   - Ran a **local scrub** SQL to clear Craft runtime state:
     - `TRUNCATE` **sessions**, **tokens**, **queue**.
     - Mass-updated non-admin user emails to a safe domain in local env (keeps uniqueness; avoids accidental emails).
   - Adjusted commands to use the `DB_` prefix (not `MYSQL_`) for env vars in the shell workflow following the legacy pattern.
3. **File System Review**
   - Checked for obvious webroot anomalies (unexpected `.php` in asset dirs, stray `composer2.phar`-style droppers, etc.).
   - Rebuilt any missing compiled assets on a clean local environment (Docker) to remove artifacts left by a compromised build chain.
4. **HTTP Layer Hardening**
   - Added **.htaccess** rules to quickly 403 common probes (e.g., `/wp-login.php`, `/xmlrpc.php`, PHPUnit, composer files) and block “nasty” query-string patterns often used by scanners.
   - Noted that `Options -Indexes` triggered **HTTP 500** on the current host (likely an Apache config/AllowOverride mismatch). I **removed** that directive and kept the rest of the rules.

---

## 4) Root Cause of Brownouts on Old Hosting
- **Primary cause:** A **“heavy template + cold cache”** pattern in Craft.
  - Expensive templates/queries are slow when caches are cold.
  - Under peak traffic, this **amplifies** to timeouts and brownouts.
- **Compounding factors:**
  - **Outdated Craft + plugins** → slower code paths & known vulnerabilities.
  - **Bot traffic** hitting heavy pages or search endpoints increases load.
  - Any residual compromise risks can further degrade performance (e.g., injected logic, spammy requests).

> Key insight I shared with the client (Sept 18, 2025): This problem can crash **any** host if you combine heavy templates, cold caches, and traffic spikes—especially with an outdated stack. I also confirmed that basic security hardening and cleanup helps, but it **won’t fully fix** brownouts without performance work and updates.

---

## 5) Mitigations
- **Security & Cleanse**
  - ✅ Rebuilt `vendor/` from lockfile (removes any injected PHP in dependencies).
  - ✅ DB/session scrub to eliminate risky tokens and stale runtime state.
  - ✅ .htaccess probe-blocking and query-string filtering (kept rules that don’t trip 500s).
- **Stability & Performance**
  - ✅ Local Docker environment to replicate and debug safely.
  - ✅ GitHub version control built with separate environments for **Production**, **Staging** and **Local Development** implemented.
  - ✅ Identified heavy-template/cold-cache pattern as the leading cause of brownouts.
  - ✅ Servd hosting connected via **Webhooks** with **Production and Staging** environments. 
  - ➕ Recommended caching/eager-loading + index warming; partial hardening was implemented, but full template/caching refactors remain pending.
- **What didn’t work or had caveats**
  - ❌ The `Options -Indexes` directive caused a **500 error** on Arcustech; I removed it for compatibility and pursued non-breaking hardening rules.

---

## 6) Final Resolution Path (Securing the site and stopping brownouts)
**Security hardening baseline (completed/ongoing):**
- Reinstall dependencies cleanly, lock Composer, keep `vendor/` out of VCS. This will be a standard procedure with any codebase update.
- Maintain `.htaccess` probe/scan blocking rules compatible with the host. Scheduled to update with each Craft update (v4 and v5).
- Keep a clean DB: clear sessions/tokens/queues after incidents; rotate secrets is standard security procedure but will likely only be needed if a security breach occurs again. Implement procedures, both automated and manual, to test DB for common signs of malicious code or modification.

**Performance fixes (to stop brownouts):**
1. **Craft & Plugin Updates**
   - Upgrade Craft and plugins to current supported versions (security + performance).
2. **Template Refactors + Eager Loading**
   - Identify worst offenders; apply eager loading; eliminate N+1 queries; memoize expensive functions.
3. **Caching Strategy**
   - Layered caching: element/query caches; fragment caches; page-level caching where feasible.
   - **Cache warming** after deploys and on schedule (cron/queue) to avoid cold-start thundering herds.
4. **Traffic Controls**
   - Bot rate-limiting at the edge (firewall/CDN) and robots adjustments.
   - Throttle or 403 abusive patterns found in access logs.
5. **Observability**
   - Centralized logs; slow query logging; baseline performance metrics to verify improvements.

**Hosting posture:**
- While partial mitigations helped, the brownouts were fundamentally **load + cold-cache** driven. The recommended lasting fix is **updates + caching + refactors**, which will stabilize the site on any host and is especially effective when combined with a modern hosting pipeline.

---

## 7) Timeline (key dates from the conversations)
- **Sept 8, 2025** — `.htaccess` hardening; discovered **`Options -Indexes` → 500** on Arcustech; retained other blocking rules.
- **Sept 15, 2025** — Malware/cleanse review; **`vendor/` removed and rebuilt**; **no custom plugins**; **zipped assets** supplied; **DB scrub** steps refined (use `DB_` env vars); worked through `mysqldump` privilege error locally; guidance to **remove `.sql` from commits**.
- **Sept 17, 2025** — Git history cleanup commands to drop committed `.sql` files (pre-push).
- **Sept 18, 2025** — Brownout analysis for client: **heavy template + cold cache** root cause explained; **DB & file cleanup + basic hardening** completed; emphasized **Craft updates + caching/eager-loading** as the durable fix.

---

## 8) Key Takeaways
1. **Treat inherited `vendor/` as untrusted** after a suspected compromise—rebuild from the lockfile.
2. **Scrub runtime state** (sessions/tokens/queue) and rotate secrets when cleaning up an incident.
3. **Harden without breaking**: some Apache directives (e.g., `Options -Indexes`) may 500 on shared hosts—prefer portable rules first.
4. **Brownouts rarely have a single cause**: outdated CMS + heavy templates + cold caches + bot traffic = instability on *any* host.
5. **Performance work is security work**: faster, cached page paths reduce exposed attack surface and DDOS-like effects from routine traffic spikes.
6. **Make cache warming part of the deploy** to avoid thundering herds and “post-deploy brownouts.”

---
