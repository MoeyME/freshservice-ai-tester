# Dahlsens IT Support Priority Matrix

## ITIL Incident Priority Matrix
### Service Desk Reference Guide
Complete guide to incident priority determination using Impact and Urgency assessment

---

## Table of Contents
1. [Priority Determination Process](#priority-determination-process)
2. [Assessment Criteria](#assessment-criteria)
3. [Type Definitions](#type-definitions)
4. [Priority Matrix](#priority-matrix)
5. [Priority Level Guidelines](#priority-level-guidelines)
6. [Service Level Agreements](#service-level-agreements)
7. [Quick Reference Guide](#quick-reference-guide)

---

## 1. Priority Determination Process

Follow this simple 3-step process to accurately determine incident priority using the ITIL framework:

### Step 1: Assess Impact
How many users, systems, or business functions are affected by this incident?

### Step 2: Evaluate Urgency
How quickly must this issue be resolved to minimize business disruption?

### Step 3: Determine Priority
Use the matrix below to find where Impact and Urgency intersect

---

## 2. Assessment Criteria

### Impact Levels

**🔴 High Impact**
- Multiple users/systems affected
- Critical business functions impacted
- Significant revenue or reputation risk

**🟠 Medium Impact**
- Limited users/systems affected
- Some business impact
- Moderate disruption to operations

**🟢 Low Impact**
- Single user/system affected
- Minimal business impact
- Isolated incident

### Urgency Levels

**🔴 High Urgency**
- Immediate resolution required
- Operations completely halted
- Cannot wait

**🟠 Medium Urgency**
- Quick resolution needed
- Significant disruption
- Should be addressed soon

**🟢 Low Urgency**
- Can be scheduled
- Minimal disruption
- Flexible timing

---

## 3. Type Definitions

### Incident
**Definition:** An unplanned interruption to an IT service or reduction in the quality of an IT service.

**Characteristics:**
- Something is broken, not working, or malfunctioning
- Represents a disruption to normal operations
- Requires troubleshooting and fixing
- Focus is on restoring normal service as quickly as possible

**Examples:**
- System crashes or errors
- Network connectivity issues
- Hardware failures
- Software not functioning correctly
- Service outages or degradation
- Users unable to access systems they normally can access

---

### Service Request
**Definition:** A formal request from a user for something to be provided - such as information, advice, access, or a standard change.

**Characteristics:**
- Something new is being requested
- Asking for information, access, or standard service
- Not a disruption - normal fulfillment process
- No troubleshooting required, just delivery of service
- Can be pre-approved and standardized

**Examples:**
- Password resets
- New user account creation
- Access requests (email, folders, applications)
- Hardware requests (keyboard, mouse, peripherals)
- Software installation requests
- Information requests
- Loan device requests
- Standard configuration changes

---

## 4. ITIL Priority Matrix

| Impact ↓ \ Urgency → | 🔴 High Urgency | 🟠 Medium Urgency | 🟢 Low Urgency |
|----------------------|-----------------|-------------------|----------------|
| **🔴 High Impact**   | **Priority 1** URGENT | **Priority 2** HIGH | **Priority 3** MEDIUM |
| **🟠 Medium Impact** | **Priority 2** HIGH | **Priority 3** MEDIUM | **Priority 4** LOW |
| **🟢 Low Impact**    | **Priority 3** MEDIUM | **Priority 4** LOW | **Priority 4** LOW |

---

## 5. Priority Level Guidelines

### Priority 1 - URGENT
**CRITICAL INCIDENT**

**Type:** Incident  
**Response:** Immediate action required. Critical business operations are halted.

**Examples:**
- Entire site network is down
- VPN is inaccessible for all users
- All POS systems offline at one or more sites
- ERP (Framework) unavailable for all users or across an entire site

---

### Priority 2 - HIGH
**MAJOR INCIDENT**

**Type:** Incident  
**Response:** Quick resolution needed to avoid major disruption to operations.

**Examples:**
- One POS unit down (others still working)
- One PC experiencing blue screens or unable to boot
- Production-critical device offline
- One EFTPOS terminal not functioning
- Site-wide network slowness
- Estimator or Detailer workstation not working
- Reception printer offline at a site

---

### Priority 3 - MEDIUM
**STANDARD INCIDENT**

**Type:** Incident or Service Request  
**Response:** Issue affects work but does not halt operations. Should be addressed within a reasonable timeframe.

**Examples:**

**Incidents:**
- Laptop or desktop intermittently rebooting
- Secondary monitor not functioning
- Printer issues not affecting critical workflows
- PDA device not working

**Service Requests:**
- New user account setup
- Request for access to former employee's email or files

---

### Priority 4 - LOW
**SERVICE REQUEST**

**Type:** Service Request  
**Response:** Minimal disruption to operations. Can be scheduled or grouped with other work.

**Examples:**
- Peripheral requests (keyboard, mouse, laptop charger, headset, camera)
- General performance issues (e.g., slow laptop)
- Password reset
- Mobile phone troubleshooting
- Request for loan devices
- Issues with non-critical software (Teams, Adobe Acrobat)
- General software installations
- VPN access issue affecting only one user

---

## 6. Service Level Agreements

| Priority Level | Response Time | Resolution Time | Working Hours |
|----------------|---------------|-----------------|---------------|
| **Priority 1 - URGENT** | 1 hour | 4 hours | Business Hours |
| **Priority 2 - HIGH** | 4 hours | 8 hours | Business Hours |
| **Priority 3 - MEDIUM** | 8 hours | 60 hours | Business Hours |
| **Priority 4 - LOW** | 10 hours | 120 hours | Business Hours |

---

## 7. Quick Reference Guide

### Priority Matrix Quick Rules

- **⚠️ Priority 1:** High Impact + High Urgency (Always Incident)
- **🔥 Priority 2:** High + Medium or Medium + High (Always Incident)
- **⚡ Priority 3:** Other Medium/Low combinations (Incident or Service Request)
- **✅ Priority 4:** Low Impact + Low Urgency (Typically Service Request)

### Type Quick Rules

**Ask yourself:**
- **"Is something broken?"** → Incident
- **"Are they asking for something new?"** → Service Request

---

**Document Authority:** Service Desk Team  
**Created:** July 2025 | **Last Updated:** October 2025  
**Version:** 1.0 | **Classification:** Internal Use