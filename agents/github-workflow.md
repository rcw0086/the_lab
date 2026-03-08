# GitHub Workflow Reference for Claude Code

This document provides explicit instructions for Claude Code to interact with GitHub Issues and the Kanban board. **All agents must follow these procedures exactly.**

---

## Critical Rules

1. **Every issue must have a Status** — No issue should exist without being in a Kanban column
2. **Update GitHub in real-time** — Move issues and check off items AS work happens, not after
3. **No task is complete without GitHub update** — Code changes alone do not constitute completion

---

## Project Board Reference

- **Project Number:** 2
- **Owner:** rcw0086
- **Repository:** rcw0086/the_lab

---

## Status Field Values

| Column | When to Use |
|--------|-------------|
| Backlog | Initial creation; not yet ready for work |
| Refined | Requirements clear; ready to be picked up |
| In-Progress | Actively being worked on |
| Review | Code complete; awaiting review |
| QA | Review passed; awaiting QA validation |
| Done | All acceptance criteria verified |
| Deployed | Released to production |

---

## Required GitHub CLI Commands

### When Creating an Issue

**Always** set the Status to Backlog immediately after creation:

```bash
# Create issue
gh issue create --repo rcw0086/the_lab --title "@DO — User Story — Task Name" --label "@DO" --body "..."

# Get the issue number from output, then add to project with Backlog status
gh project item-add 2 --owner rcw0086 --url "https://github.com/rcw0086/the_lab/issues/NUMBER"

# Set status to Backlog (get item ID first)
gh project item-list 2 --owner rcw0086 --format json | jq '.items[] | select(.content.number == NUMBER) | .id'

gh project item-edit --project-id PVT_kwHOALRmDc4BM53F --id ITEM_ID --field-id PVTSSF_lAHOALRmDc4BM53Fzg8DYxY --single-select-option-id BACKLOG_OPTION_ID
```

### When Starting Work on an Issue

**Before writing any code**, move the issue to In-Progress:

```bash
# Move to In-Progress
gh project item-edit --project-id PVT_kwHOALRmDc4BM53F --id ITEM_ID --field-id PVTSSF_lAHOALRmDc4BM53Fzg8DYxY --single-select-option-id INPROGRESS_OPTION_ID

# Add a comment noting work has started
gh issue comment NUMBER --repo rcw0086/the_lab --body "Starting work on this task. Operating as: [Agent Role]"
```

### When Completing a Checklist Item

Update the issue body to check off completed items:

```bash
# Get current issue body, update checkbox from [ ] to [x], then update
gh issue edit NUMBER --repo rcw0086/the_lab --body "UPDATED_BODY_WITH_CHECKED_ITEMS"
```

### When Work is Complete

1. Move to Review status
2. Post completion summary as comment
3. Link any PRs

```bash
# Move to Review
gh project item-edit --project-id PVT_kwHOALRmDc4BM53F --id ITEM_ID --field-id PVTSSF_lAHOALRmDc4BM53Fzg8DYxY --single-select-option-id REVIEW_OPTION_ID

# Post completion summary
gh issue comment NUMBER --repo rcw0086/the_lab --body "$(cat <<'EOF'
## Completion Summary

**What I did:**
- [List of completed items]

**Why:**
- [Rationale]

**Tradeoffs:**
- [Any tradeoffs made]

**Risks:**
- [Known risks or "None identified"]

**Definition of Done status:**
- [x] Scope documented
- [x] Tests exist
- [x] Docs updated
- etc.

**Next steps:**
- Move to QA for validation
EOF
)"
```

---

## Workflow Checklist for Agents

### Before Starting Any Work

- [ ] Identify the GitHub issue to work on
- [ ] Verify issue is in Refined or assigned to you
- [ ] Move issue to In-Progress
- [ ] Post comment: "Starting work. Operating as: [Role]"

### During Work

- [ ] Check off completion criteria as each is met (edit issue body)
- [ ] Post progress comments for significant milestones
- [ ] Link commits/PRs to the issue

### After Completing Work

- [ ] Verify all completion criteria are checked
- [ ] Post completion summary comment (use template above)
- [ ] Move issue to Review
- [ ] Ensure PR references the issue number

### Never Do

- ❌ Create issues without setting Status to Backlog
- ❌ Start coding without moving issue to In-Progress
- ❌ Complete work without posting summary to GitHub
- ❌ Consider a task "done" if GitHub isn't updated

---

## Project Field IDs (Reference)

These IDs are needed for `gh project item-edit` commands:

- **Project ID:** `PVT_kwHOALRmDc4BM53F`
- **Status Field ID:** `PVTSSF_lAHOALRmDc4BM53Fzg8DYxY`

### Status Option IDs

| Status | Option ID |
|--------|-----------|
| Backlog | `566b43d5` |
| Refined | `c36804f8` |
| In-Progress | `ba039d6f` |
| Review | `0a9b80ca` |
| QA | `ca5048d6` |
| Done | `f2abef06` |
| Deployed | `1f43fb81` |

To refresh these IDs if the board is recreated:
```bash
gh project field-list 2 --owner rcw0086 --format json
```

---

## Example: Complete Task Workflow

```bash
# 1. Issue #8 exists in Backlog. Starting work.

# Get project item ID for issue #8
gh project item-list 2 --owner rcw0086 --format json
# Find the item with content.number == 8, note its "id" field (e.g., "PVTI_xxx")

# Move to In-Progress
gh project item-edit --project-id PVT_kwHOALRmDc4BM53F --id PVTI_xxx --field-id PVTSSF_lAHOALRmDc4BM53Fzg8DYxY --single-select-option-id ba039d6f

# Post start comment
gh issue comment 8 --repo rcw0086/the_lab --body "Starting work. Operating as: DevOps Agent"

# ... do the work ...

# Check off completion criteria by editing issue body
gh issue view 8 --repo rcw0086/the_lab --json body
# Update [ ] to [x] for completed items, then:
gh issue edit 8 --repo rcw0086/the_lab --body "UPDATED_BODY"

# Post completion summary
gh issue comment 8 --repo rcw0086/the_lab --body "## Completion Summary ..."

# Move to Review
gh project item-edit --project-id PVT_kwHOALRmDc4BM53F --id PVTI_xxx --field-id PVTSSF_lAHOALRmDc4BM53Fzg8DYxY --single-select-option-id 0a9b80ca

# After QA passes, move to Done
gh project item-edit --project-id PVT_kwHOALRmDc4BM53F --id PVTI_xxx --field-id PVTSSF_lAHOALRmDc4BM53Fzg8DYxY --single-select-option-id f2abef06
```

---

## Failure Modes to Avoid

| Failure | Consequence | Prevention |
|---------|-------------|------------|
| Issues created without Backlog status | Board shows incomplete picture | Always run status update after issue creation |
| Work started without In-Progress | No visibility into active work | Move status BEFORE writing code |
| Completion criteria not checked off | Unclear what's done | Check off items one-by-one as completed |
| No completion summary posted | Lost context for future sessions | Always post summary using template |
| Status not moved to Review/Done | Stale board, confusion | Update status as final step of each task |
