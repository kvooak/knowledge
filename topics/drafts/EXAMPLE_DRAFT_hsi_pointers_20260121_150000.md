# Topic: HSI pointers

> **Status**: DRAFT
> **Created**: 2026-01-21T15:00:00.000000+00:00
> **Last Updated**: 2026-01-21T15:00:00.000000+00:00
> **Reviewed By**: NOT REVIEWED

---

## Definition

**Primary Definition**:
The Horizontal Situation Indicator (HSI) format on the DU is a compass rose that shows heading, course, and track information. The HSI provides lubber line heading, a heading readout, selected heading bug, compass reference marks, course pointer, lateral deviation bar, scale, and to/from arrow.

**Source**: [Operators Guide - PL Fusion_chunk_0171, Operators Guide - PL Fusion, p.159]

**Synonym(s)**: NOT SPECIFIED

---

## Related Terms

| Term | Relationship | Source |
|------|--------------|--------|
| DU (Display Unit) | uses | [glossary.md] |
| ADI (Attitude Director Indicator) | related-display | [glossary.md] |
| FMS (Flight Management System) | provides-data-to | [glossary.md] |
| CDI (Course Deviation Indicator) | component-of | [glossary.md] |

---

## Sources

### Primary Sources
- Operators Guide - PL Fusion, Section: HSI Format, p.159-163
- Operators Guide - PL Fusion, Section: Navigation Displays, p.107-115
- Operators Guide - PL Fusion, Section: Display Formats, p.56-70

**Coverage Assessment**: PARTIAL (draft)
**Confidence**: MEDIUM (draft - requires verification)

---

## Rules

### Conditional Behaviors (IF/WHEN -> THEN)

#### Rule 1: HSI Display Modes
**Condition**: WHEN HSI format is selected
**Consequence**: THEN display shows one of 3 states: CDI indications with overlays, FMS map indications with overlays, or Clean HSI (all overlays removed)
**Source**: [Operators Guide - PL Fusion, p.159]
**Certainty**: EXPLICIT

#### Rule 2: Course Pointer Display
**Condition**: WHEN navigation source is active
**Consequence**: THEN course pointer indicates selected course with lateral deviation bar showing deviation from course
**Source**: [Operators Guide - PL Fusion, p.160]
**Certainty**: EXPLICIT

---

## Behavior

### Normal Operation
The HSI displays as a compass rose with the following components:
- Lubber line heading at top center
- Heading readout (digital)
- Selected heading bug (magenta triangle)
- Compass reference marks (every 30 degrees)
- Course pointer (indicates selected course)
- Lateral deviation bar (shows deviation from course)
- Scale indication (for deviation sensitivity)
- To/from arrow (indicates whether flying to or from the navigation point)

**Source**: [glossary.md, Operators Guide - PL Fusion, p.159]

### States/Modes
| State/Mode | Description | Trigger | Source |
|------------|-------------|---------|--------|
| CDI Mode | Course Deviation Indicator with overlays | Navigation source selected | [Operators Guide, p.159] |
| FMS Map Mode | Moving map with FMS flight plan overlays | FMS mode selected | [Operators Guide, p.160] |
| Clean HSI | Basic compass rose without overlays | Clean mode selected | [Operators Guide, p.159] |

---

## Limitations

### Explicit Constraints
1. The HSI format can only be displayed on designated Display Units (DU1 or DU3)
   **Source**: [Operators Guide - PL Fusion, p.107]

2. HSI display requires valid heading source from AHRS
   **Source**: [Operators Guide - PL Fusion, p.35]

### Boundary Conditions
NOT SPECIFIED IN SOURCE (requires manual verification from source documents)

---

## Procedures

### Selecting HSI Format

**Purpose**: Display HSI on designated Display Unit
**Source**: synth/procedures/ (if exists)

**Steps**:
1. Press FORMAT button on CCP (Cursor Control Panel)
2. Select HSI format from menu
3. Confirm selection

(NOTE: Complete procedure requires verification from source document)

**Preconditions**: Valid heading source available
**Expected Outcome**: HSI format displayed on selected DU

---

## Edge Cases

### Documented Edge Cases
1. **Heading Source Failure**
   **Condition**: AHRS heading source becomes invalid
   **Behavior**: HSI displays "HDG" flag and compass rose freezes
   **Source**: [Operators Guide - PL Fusion, p.35]

2. **Navigation Source Loss**
   **Condition**: Navigation source signal lost
   **Behavior**: Course pointer and lateral deviation bar removed, "NAV" flag displayed
   **Source**: [Operators Guide - PL Fusion, p.160]

---

## Open Questions

> These are gaps in documentation, NOT assumptions or inferences.

1. **What is the exact sensitivity scaling for the lateral deviation bar?**
   **Why this matters**: Pilots need to know deviation sensitivity for different flight phases
   **Search attempted**: glossary.md, rules.md, procedures/, chunks mentioning "deviation scale"
   **Result**: Referenced but not explicitly defined

2. **Are there different HSI formats for different navigation modes (GPS vs VOR vs ILS)?**
   **Why this matters**: Understanding mode-specific displays
   **Search attempted**: Searched for "HSI GPS", "HSI VOR", "HSI ILS" in chunks
   **Result**: Multiple references but complete behavior not synthesized

3. **What happens during display reversion?**
   **Why this matters**: Understanding backup display behavior
   **Search attempted**: Searched for "HSI reversion" in rules.md and chunks
   **Result**: General reversion mentioned but HSI-specific behavior not detailed

4. **Course pointer vs heading bug - when are they the same vs different?**
   **Why this matters**: Understanding pilot inputs and displayed values
   **Search attempted**: glossary.md, procedural documents
   **Result**: Both mentioned but relationship not explicitly defined

---

## Verification Status

- [ ] All citations verified against source documents
- [ ] All "NOT SPECIFIED" claims verified (absence confirmed)
- [ ] No inferences or assumptions present
- [ ] Related terms cross-referenced
- [ ] Open questions documented
- [ ] Human review completed

**Reviewer Notes**:
This draft was generated from existing curated knowledge (glossary.md) and raw chunk search.
Requires manual review of source PDF sections 3.2 (Displays) and 4.5 (Navigation) for completeness.

**Action Items for Human Reviewer**:
1. Verify HSI mode transitions (CDI -> FMS Map -> Clean)
2. Document deviation scale sensitivity values
3. Complete procedure steps with source verification
4. Resolve all Open Questions from source documents
5. Verify edge cases are comprehensive

---

## Metadata

**Source Documents Analyzed**:
- Operators Guide - PL Fusion (E550 Collins)

**Chunks Analyzed**: 15 chunks containing "HSI" mentions
**Generated By**: topic_draft.py v1.0.0 (MANUAL EXAMPLE)
**Template Version**: 1.0.0

---

**CRITICAL REMINDER**:
This topic file is a DRAFT generated from curated knowledge files.
It requires human review before promotion to authoritative status.
DO NOT treat this as authoritative knowledge.

**To Promote to Curated**:
1. Complete all verification checklist items
2. Resolve all Open Questions
3. Verify all citations against source PDF
4. Move to `topics/hsi_pointers.md`
5. Update Status to CURATED
6. Set Reviewed By field
7. Commit with review notes
