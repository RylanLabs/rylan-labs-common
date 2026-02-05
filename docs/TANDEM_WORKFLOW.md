# IRL-First Approach: Manual Before Automated

> **⚠️ ABSORBED**: This document has been absorbed into [GITOPS-SUBSTRATE-PARADIGM.md](GITOPS-SUBSTRATE-PARADIGM.md) Section 1.
> This file is retained for historical reference and backward compatibility.
> For canonical guidance, see the master paradigm document.

> Canonical philosophy — RylanLabs eternal standard
> Version: v2.0.0
> Date: 2026-01-13
> **Status**: Experimental (Applying these principles to rylan-labs-common)

---

!!! info "Operational Context"
    This document describes the *ideal* workflow we follow.
    For the `rylan-labs-common` repository, we are currently in
    **Phase 4 (Introduce Light Automation)** of this process.
    Some "Hard Gates" are in place but security and test coverage are
    still being manually matured.

## Overview

The **IRL-First (In Real Life First) approach** prioritizes human understanding and manual validation before introducing automated enforcement.

This philosophy ensures that discipline systems **serve developers** rather than constrain them. It answers the question: *How do we build sustainable discipline that people choose to follow, not rules they resent?*

**Core principle**: Understand the "why" before automating the "how."

---

## Philosophy

### Human Understanding First

**Why this matters**: Blind automation creates fragility. When operators don't understand *why* a rule exists, they bypass it.

**Real example from rylan-unifi-case-study**:

- Early attempt: Enforce mypy strict mode via pre-commit hook
- Result: Developers added `# type: ignore` everywhere
- Problem: Type safety defeated, but technically "compliant"
- Solution: Teach *why* type safety matters (catches entire classes of bugs)
- Outcome: Developers voluntarily adopted mypy strict, 44→0 errors

**Lesson**: Enforcement without understanding creates resentment. Understanding creates buy-in.

**Implementation**:

1. Document the principle (not just the rule)
2. Show real examples of why it matters
3. Demonstrate impact (before/after metrics)
4. Let people practice before enforcing
5. Answer "why" questions, don't dismiss them

### Manual Validation Phase

**Why this matters**: Manual practice builds intuition. Intuition enables judgment calls.

**Real example from firewall-consolidation**:

- Early attempt: Automate firewall rule generation
- Result: Generated 47 rules, many redundant
- Problem: Automation doesn't understand business context
- Solution: Manually design rules, understand each one
- Outcome: Consolidated to 10 rules, all justified, hardware-aware

**Lesson**: Automation amplifies understanding, but can't replace it.

**Implementation**:

1. Perform the task manually first (even if slow)
2. Document each decision and rationale
3. Identify patterns (what repeats?)
4. Only then automate the patterns
5. Keep manual override for edge cases

### Gradual Automation

**Why this matters**: Automation introduced gradually is easier to debug and understand.

**Real example from CI/CD maturation**:

- Phase 1: Manual pre-commit validation (developer runs shellcheck)
- Phase 2: Pre-commit hook (automatic, but can bypass with --no-verify)
- Phase 3: CI gate (blocks merge if validation fails)
- Phase 4: Gatekeeper (pre-receive hook, no bypass possible)
- Result: Discipline scaled without resentment

**Lesson**: Each automation layer should be understandable before the next is introduced.

**Implementation**:

1. Start with manual (documented steps)
2. Add helper tools (make it easier)
3. Add soft gates (warnings, not blocks)
4. Add hard gates (blocks, but with clear remediation)
5. Add monitoring (continuous validation)

### Maintained Human Oversight

**Why this matters**: Automation can't handle all edge cases. Humans provide judgment.

**Real example from rylan-unifi-case-study**:

- Situation: Type safety rule caught legitimate use case
- Automated response: Block merge
- Human response: Review exception, document rationale, approve
- Outcome: Rule refined, exception documented, learning preserved

**Lesson**: Automation should inform humans, not replace them.

**Implementation**:

1. All critical operations require human confirmation
2. Automation provides context (what changed, why it matters)
3. Humans make final decision
4. Decision is audited (git commit, timestamp, rationale)
5. Exceptions are documented and reviewed

---

## The IRL-First Process (5 Phases)

### Phase 1: Learn Principles

**Duration**: 1-2 weeks (for new operator or new domain)
**What happens**:

- Read documentation (why does this matter?)
- Study real examples (how has this been applied?)
- Ask questions (what doesn't make sense?)
- Understand rationale (not just rules)

**Success criteria**:

- Can explain the principle in own words
- Can identify why it matters
- Can ask intelligent questions
- Understands trade-offs

**Example: Learning Bash Discipline**

```
Week 1:
- Read bash-discipline.md (why strict mode matters)
- Study real scripts (how are they structured?)
- Ask: "Why set -euo pipefail?" (not "I have to do this")
- Understand: Error handling prevents cascade failures
Success: Can explain why set -euo pipefail prevents bugs
```

### Phase 2: Practice with Feedback

**Duration**: 2-4 weeks (hands-on application)
**What happens**:

- Write code/scripts manually (no automation yet)
- Get feedback from experienced operator
- Refine based on feedback
- Repeat until consistent

**Success criteria**:

- Code demonstrates all Seven Pillars
- Feedback is positive (or constructive)
- Patterns are consistent
- Questions are decreasing

**Example: Writing First Playbook**

```
Week 1-2:
- Write bootstrap.yml manually
- Submit for review
- Feedback: "Missing error handling in task X"
- Revise: Add block/rescue/always
- Resubmit
Week 3-4:
- Write verify.yml
- Feedback: "Good error handling, add audit logging"
- Revise: Add structured logging
- Resubmit: Approved
Success: Can write playbooks that pass review consistently
```

### Phase 3: Validate Understanding

**Duration**: 1-2 weeks (demonstrate competence)
**What happens**:

- Execute task independently (no guidance)
- Explain decisions made
- Handle edge cases
- Document process

**Success criteria**:

- Task completed without assistance
- Decisions align with principles
- Edge cases handled appropriately
- Documentation is clear

**Example: Independent Deployment**

```
Scenario: Deploy new service to production
Operator:
1. Writes playbook independently
2. Runs --check mode (validates logic)
3. Explains each task (why this way?)
4. Handles error case (what if X fails?)
5. Documents rollback procedure
6. Gets approval from senior operator
Success: Deployment completes, all decisions justified, no surprises
```

### Phase 4: Introduce Light Automation

**Duration**: 1-2 weeks (helpers, not gatekeepers)
**What happens**:

- Add helper tools (make manual work easier)
- Add warnings (suggest improvements)
- Add soft gates (informational, not blocking)
- Operator can still override

**Success criteria**:

- Tools are helpful, not frustrating
- Operator understands what tools do
- Operator can override when needed
- Overrides are documented

**Example: Pre-Commit Hooks**

```
Phase 4a: Helper tool
- shellcheck runs on commit
- Shows warnings
- Operator can fix or override
Phase 4b: Soft gate
- Pre-commit hook runs
- Blocks commit if critical errors
- But operator can --no-verify if justified
- Override is logged
Success: Operator uses tool voluntarily, understands when to override
```

### Phase 5: Scale Thoughtfully

**Duration**: Ongoing (automation with escape hatches)
**What happens**:

- Hard gates introduced (CI/CD, pre-receive hooks)
- Escape hatches remain (documented, audited)
- Monitoring tracks compliance
- Exceptions are reviewed

**Success criteria**:

- Automation catches 80% of issues locally
- Hard gates prevent 95% of bad merges
- Escape hatches are rarely used
- Culture supports discipline

**Example: Full CI/CD Pipeline**

```
Phase 5a: Pre-commit (local, can override)
- Catches: syntax, linting, basic security
- Override: --no-verify (logged)
Phase 5b: CI gates (remote, harder to bypass)
- Catches: type safety, security scans, tests
- Override: Requires manual approval (audited)
Phase 5c: Pre-receive hooks (production, no bypass)
- Catches: policy violations, audit trail gaps
- Override: Requires Trinity consensus (documented)
Success: 80% of issues caught locally, 95% caught before merge,
         100% caught before production, culture supports discipline
```

---

## Balancing Automation and Flexibility

### When to Automate

**Automate when**:

1. **Pattern is clear** — Repeats consistently across projects
2. **Cost is high** — Manual process is error-prone or time-consuming
3. **Understanding is deep** — Team understands why rule exists
4. **Escape hatches exist** — Override mechanism is documented
5. **Monitoring is in place** — Can detect when automation fails

**Real example: Pre-commit validation**

- Pattern: Every script needs shellcheck validation (clear)
- Cost: Manual validation is slow + error-prone (high)
- Understanding: Team knows why shellcheck matters (deep)
- Escape hatch: `shellcheck disable` for justified exceptions (exists)
- Monitoring: CI catches any skipped checks (in place)
- **Result**: Automate pre-commit hook

### When to Keep Manual

**Keep manual when**:

1. **Pattern is unclear** — Varies by context
2. **Judgment is required** — Can't codify decision
3. **Cost of false positives is high** — Automation might block legitimate work
4. **Understanding is shallow** — Team still learning why rule exists
5. **Escape hatches are complex** — Override mechanism would be confusing

**Real example: Code review**

- Pattern: Varies by context (unclear)
- Judgment: Requires human expertise (required)
- Cost: Automation might reject valid patterns (high)
- Understanding: Still evolving (shallow)
- Escape hatch: Would be confusing (complex)
- **Result**: Keep manual (experienced operator reviews)

### Escape Hatches (Override Mechanisms)

**Escape hatches are not failures** — they're safety valves.

**When escape hatches are used**:

- Legitimate edge case discovered
- Rule needs refinement
- Learning opportunity

**How escape hatches work**:

```bash
# Example 1: Pre-commit override (soft gate)
git commit --no-verify
# BUT: Logged in git history, visible to team
# AND: CI will catch it anyway (hard gate)
# Example 2: CI override (medium gate)
# Requires manual approval from senior operator
# Approval is audited (git commit + timestamp)
# Exception is documented in eternal-glue.md
# Example 3: Pre-receive override (hard gate)
# Requires Trinity consensus (Carter + Bauer + Beale)
# Decision is documented + committed
# Exception is reviewed quarterly
```

**Escape hatch principles**:

1. **Visible** — Override is logged, not hidden
2. **Audited** — Who, when, why is recorded
3. **Documented** — Rationale is preserved
4. **Reviewed** — Exceptions are analyzed for patterns
5. **Refined** — Rules are updated based on exceptions

---

## Anti-Patterns (What Not to Do)

### Anti-Pattern 1: Automation Too Early

**What happens**:

- Automate before understanding is deep
- Rules are too strict or too loose
- Developers resent the automation
- Bypass culture emerges

**Real example from early rylan-unifi-case-study**:

```
Mistake: Enforce mypy strict mode via pre-commit hook
         before team understood type safety
Result:
- Developers added # type: ignore everywhere
- Type safety defeated (technically compliant)
- Resentment toward automation
- Bypass culture emerged
Fix: Remove automation, teach principles first
     After 2 weeks of manual practice:
     - Team understood why type safety matters
     - Developers voluntarily adopted mypy strict
     - 44→0 errors (organic, not forced)
     - No resentment, strong buy-in
```

**How to avoid**:

1. Teach principles first (1-2 weeks)
2. Practice manually (2-4 weeks)
3. Validate understanding (1-2 weeks)
4. Only then automate (Phase 4+)

### Anti-Pattern 2: Enforcement Without Context

**What happens**:

- Rules are enforced without explanation
- Developers don't understand why
- Bypass culture emerges
- Rules become cargo cult

**Real example from firewall-consolidation**:

```
Mistake: Enforce "max 10 firewall rules" without context
Result:
- Team didn't understand why 10 was chosen
- Legitimate rules were deleted to meet quota
- Security was compromised
- Rule was meaningless
Fix: Explain the context (hardware constraints, performance)
     Show the trade-offs (fewer rules = faster processing)
     Validate together (measure impact of each rule)
     Rule becomes meaningful
```

**How to avoid**:

1. Document the "why" (not just the rule)
2. Show real examples (before/after)
3. Explain trade-offs (what's the cost?)
4. Let team practice (build intuition)
5. Answer questions (don't dismiss concerns)

### Anti-Pattern 3: No Path Forward

**What happens**:

- Automation blocks legitimate work
- No override mechanism exists
- Developers are stuck
- Bypass culture emerges

**Real example from early CI/CD attempts**:

```
Mistake: CI gate blocks merge if coverage < 80%
         No override mechanism exists
Result:
- Developer writes legitimate code (coverage 78%)
- CI blocks merge (no way to proceed)
- Developer is stuck (can't ship)
- Bypass culture emerges (CI gets disabled)
Fix: Add override mechanism with audit trail
     Developer can request override
     Senior operator reviews + approves
     Override is documented + audited
     Exception is reviewed quarterly
```

**How to avoid**:

1. Always provide override mechanism
2. Make override visible + audited
3. Document rationale for override
4. Review exceptions quarterly
5. Refine rules based on exceptions

---

## Implementation Strategies

### Strategy 1: Onboarding New Operators

**Goal**: New operator understands discipline and can execute independently
**Timeline**: 4-6 weeks

**Week 1: Learn Principles**

- Read: seven-pillars.md, eternal-glue.md, bash-discipline.md
- Study: Real examples from rylan-unifi-case-study
- Ask: Questions about rationale
- Deliverable: Written summary of principles

**Week 2-3: Practice with Feedback**

- Task 1: Write a simple bash script (with review)
- Task 2: Write a simple playbook (with review)
- Task 3: Deploy a service (with guidance)
- Deliverable: Scripts/playbooks that pass review

**Week 4: Validate Understanding**

- Task: Execute deployment independently
- Explain: Each decision made
- Handle: Edge cases
- Deliverable: Deployment log + documentation

**Week 5-6: Introduce Automation**

- Show: Pre-commit hooks, CI gates, monitoring
- Practice: Using tools voluntarily
- Override: When and how to override
- Deliverable: Independent deployment with automation

**Success criteria**:

- Operator can execute at 3 AM without assistance
- Decisions align with principles
- Documentation is clear
- Automation is understood, not feared

### Strategy 2: Introducing New Standards

**Goal**: Team adopts new standard without resentment
**Timeline**: 4-8 weeks

**Phase 1: Propose (Week 1)**

- Document the principle (why does this matter?)
- Show real examples (where has this helped?)
- Explain trade-offs (what's the cost?)
- Invite feedback (what concerns do you have?)

**Phase 2: Pilot (Week 2-3)**

- Volunteers practice manually
- Feedback loop with experienced operator
- Document patterns
- Refine based on feedback

**Phase 3: Validate (Week 4-5)**

- Volunteers execute independently
- Explain decisions
- Handle edge cases
- Demonstrate competence

**Phase 4: Soft Automation (Week 6)**

- Add helper tools (make manual work easier)
- Add warnings (suggest improvements)
- Add soft gates (informational, not blocking)
- Team can still override

**Phase 5: Hard Automation (Week 7-8)**

- Add hard gates (blocks, but with clear remediation)
- Escape hatches remain (documented, audited)
- Monitor compliance
- Review exceptions

**Success criteria**:

- Team understands why standard exists
- Team voluntarily follows standard
- Automation is helpful, not frustrating
- Exceptions are rare and documented

### Strategy 3: Handling Bypass Attempts

**Goal**: Address bypass culture before it takes root

**When bypass attempt is detected**:

```
Step 1: Stop the bypass
  → Pre-commit hook blocks --no-verify
  → CI gate blocks merge
  → Pre-receive hook blocks push
Step 2: Understand the reason
  → Talk to developer
  → "Why did you try to bypass?"
  → Listen to the answer
Step 3: Categorize the bypass
  → Legitimate edge case? (rule needs refinement)
  → Misunderstanding? (need more education)
  → Laziness? (need to reinforce discipline)
  → Time pressure? (need to address root cause)
Step 4: Respond appropriately
  → Edge case: Refine rule, document exception
  → Misunderstanding: Teach principles, practice together
  → Laziness: Reinforce discipline, review with team
  → Time pressure: Address project planning
Step 5: Document and review
  → Log the bypass attempt
  → Review with team (learning opportunity)
  → Update documentation if needed
  → Prevent recurrence
```

---

## Measuring Success

### Metric 1: Adoption Rate

**What to measure**: Percentage of team following standard voluntarily
**Target**: >90% voluntary adoption (without enforcement)
**How to measure**:

```bash
# Count commits that follow standard
git log --oneline | grep -c "feat\|fix\|docs\|refactor"
# Count commits that violate standard
git log --oneline | grep -c "WIP\|TODO\|FIXME"
# Calculate adoption rate
adoption_rate = (compliant_commits / total_commits) * 100
```

### Metric 2: Bypass Rate

**What to measure**: Frequency of bypass attempts (--no-verify, [ci skip], etc.)
**Target**: <1% bypass rate (exceptions are rare)
**How to measure**:

```bash
# Count bypass attempts
git log --oneline | grep -c "no-verify\|ci skip"
# Calculate bypass rate
bypass_rate = (bypass_attempts / total_commits) * 100
```

### Metric 3: Error Detection Rate

**What to measure**: Percentage of errors caught before production
**Target**: >95% errors caught before merge
**How to measure**:

```bash
# Errors caught by pre-commit
pre_commit_errors = (shellcheck + mypy + bandit) errors
# Errors caught by CI
ci_errors = (type safety + security + test) failures
# Errors caught in production
production_errors = (incidents caused by preventable errors)
# Calculate detection rate
detection_rate = ((pre_commit + ci) / (pre_commit + ci + production)) * 100
```

### Metric 4: RTO Achievement

**What to measure**: Percentage of deployments meeting <15 min RTO target
**Target**: 100% of deployments <15 min RTO
**How to measure**:

```bash
# Measure actual RTO for each deployment
deployment_time = (end_time - start_time)
# Track against target
rto_met = (deployment_time <= 15_minutes)
# Calculate achievement rate
rto_rate = (deployments_meeting_target / total_deployments) * 100
```

### Metric 5: Operator Confidence

**What to measure**: Qualitative assessment of operator confidence
**Target**: Operators can execute at 3 AM without assistance
**How to measure**:

```
Survey questions:
1. Can you execute deployment without guidance? (1-5)
2. Do you understand why each step matters? (1-5)
3. Can you handle edge cases? (1-5)
4. Would you be confident at 3 AM? (1-5)
Target: Average score 4.5+ (strongly agree)
```

---

## Common Questions

### Q: Doesn't IRL-First slow down adoption?

**A**: Short-term yes, long-term no.

**Timeline comparison**:

- **Enforcement-first**: Fast adoption (week 1), high bypass rate (8%), low buy-in
- **IRL-First**: Slower adoption (week 4), low bypass rate (0.5%), high buy-in

**6-month outcome**:

- Enforcement-first: 60% compliance (resentment, workarounds)
- IRL-First: 95% compliance (voluntary, sustainable)

### Q: What if someone refuses to learn?

**A**: Rare, but address directly.

**Process**:

1. Understand why (is it unclear? too hard? not convinced?)
2. Provide support (mentoring, pair programming, extra time)
3. Set clear expectations (this is non-negotiable)
4. Document the conversation (audit trail)
5. Escalate if needed (team lead, management)

### Q: How do we handle time pressure?

**A**: IRL-First actually saves time long-term.

**Short-term (week 1-2)**:

- Manual practice seems slow
- Temptation to skip and automate
- Resist this (discipline pays off)

**Long-term (month 2+)**:

- Manual practice pays dividends
- Operators are confident
- Automation is effective
- Fewer bugs, faster deployments

### Q: What about contractors or temporary team members?

**A**: Compress the timeline, but don't skip phases.

**Compressed timeline (2-3 weeks)**:

- Phase 1: Learn principles (3 days)
- Phase 2: Practice with feedback (5 days)
- Phase 3: Validate understanding (3 days)
- Phase 4-5: Introduce automation (2-3 days)

**Key**: Don't skip phases, just compress them. Temporary team members still need to understand discipline.

---

## The IRL-First Promise

**Problem**: Automation without understanding creates resentment, bypass culture, and fragility.
**Solution**: IRL-First approach builds understanding first, then automates thoughtfully.
**How it works**:

1. Learn principles (why does this matter?)
2. Practice manually (build intuition)
3. Validate understanding (demonstrate competence)
4. Introduce light automation (helpers, not gatekeepers)
5. Scale thoughtfully (automation with escape hatches)

**The result**:

- Operators understand discipline, not just rules
- Bypass culture doesn't emerge
- Automation serves discipline, not vice versa
- Sustainable, voluntary compliance
- Operators can execute at 3 AM with confidence

**The promise**: Discipline through understanding, not enforcement.

---

## Related Documents

- [seven-pillars.md](seven-pillars.md) — Core principles IRL-First builds on
- [eternal-glue.md](eternal-glue.md) — Sacred artifacts that IRL-First protects
- [no-bypass-culture.md](no-bypass-culture.md) — How IRL-First prevents bypass culture
- [bash-discipline.md](bash-discipline.md) — Technical standards IRL-First teaches
- [ansible-discipline.md](ansible-discipline.md) — Orchestration standards IRL-First teaches

---

## Implementation Checklist

### For Onboarding New Operators

- [ ] Week 1: Operator reads seven-pillars.md, eternal-glue.md, bash-discipline.md
- [ ] Week 1: Operator studies real examples from rylan-unifi-case-study
- [ ] Week 1: Operator writes summary of principles
- [ ] Week 2-3: Operator writes scripts/playbooks with review
- [ ] Week 3: Operator deploys service with guidance
- [ ] Week 4: Operator executes deployment independently
- [ ] Week 4: Operator explains all decisions
- [ ] Week 5-6: Operator practices with automation tools
- [ ] Week 5-6: Operator can override when needed
- [ ] Week 6: Operator is ready for 3 AM deployment

### For Introducing New Standards

- [ ] Phase 1: Document principle + show examples
- [ ] Phase 1: Explain trade-offs + invite feedback
- [ ] Phase 2-3: Volunteers practice manually
- [ ] Phase 2-3: Feedback loop with experienced operator
- [ ] Phase 4-5: Volunteers execute independently
- [ ] Phase 4-5: Demonstrate competence + handle edge cases
- [ ] Phase 6: Add helper tools (soft automation)
- [ ] Phase 7-8: Add hard gates (with escape hatches)
- [ ] Phase 8: Monitor compliance + review exceptions

### For Handling Bypass Attempts

- [ ] Stop the bypass
- [ ] Understand the reason
- [ ] Categorize the bypass
- [ ] Respond appropriately
- [ ] Document and review

---
**The fortress demands discipline. No shortcuts. No exceptions.**

IRL-First is the path to sustainable discipline.

Understanding first. Automation second.

The Trinity endures.
