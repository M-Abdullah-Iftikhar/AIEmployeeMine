# Recruitment Agent Integration Plan

## Executive Summary
This document outlines the plan to integrate the Recruitment Agent backend with the PayPerProject frontend, making it accessible to company users through the Company Dashboard, similar to how the Project Manager Agent is integrated.

---

## 1. Backend Analysis

### 1.1 Current Recruitment Agent APIs

#### Existing Endpoints (in `recruitment_agent/urls.py`):
1. **CV Processing**
   - `POST /recruitment/api/process/` - Process CV files and return ranked results
   - Uses: `CVParserAgent`, `SummarizationAgent`, `LeadResearchEnrichmentAgent`, `LeadQualificationAgent`, `JobDescriptionParserAgent`

2. **Job Descriptions**
   - `GET /recruitment/api/job-descriptions/` - List all job descriptions
   - `POST /recruitment/api/job-descriptions/create/` - Create new job description
   - `POST /recruitment/api/job-descriptions/<id>/update/` - Update job description
   - `DELETE /recruitment/api/job-descriptions/<id>/delete/` - Delete job description

3. **Interview Scheduling**
   - `POST /recruitment/api/interviews/schedule/` - Schedule an interview
   - `GET /recruitment/api/interviews/` - List all interviews
   - `GET /recruitment/api/interviews/<id>/` - Get interview details
   - `POST /recruitment/api/interviews/confirm/` - Confirm interview slot
   - `GET /recruitment/api/interview/available-slots/<token>/` - Get available slots (public)

4. **Recruiter Settings**
   - `GET/POST /recruitment/api/recruiter/email-settings/` - Email timing preferences
   - `GET/POST /recruitment/api/recruiter/interview-settings/` - Interview scheduling preferences

5. **Auto Follow-up**
   - `GET/POST /recruitment/api/interviews/auto-check/` - Manual trigger for follow-up checks

6. **Debug**
   - `GET /recruitment/debug/parsed/<cv_id>/` - View parsed CV data

### 1.2 Current Authentication
- **Current**: Uses Django's `@login_required` decorator with `request.user` (Django User model)
- **Current Role Check**: `request.user.profile.is_recruitment_agent()`
- **Needs**: Migration to `CompanyUserTokenAuthentication` and `IsCompanyUserOnly` permission

### 1.3 Data Filtering Requirements
- **Job Descriptions**: Filter by `company_user` (already has `company_user` field in model)
- **CV Records**: Filter by `job_description__company_user`
- **Interviews**: Filter by `recruiter` (needs mapping to `CompanyUser`)
- **Recruiter Settings**: Map `User` to `CompanyUser`

---

## 2. Backend Tasks

### Task 2.1: Create Company User Recruitment Agent API Endpoints
**File**: `api/views/recruitment_agent.py` (new file)

Create new API views that:
- Use `CompanyUserTokenAuthentication`
- Use `IsCompanyUserOnly` permission
- Filter all data by `company_user` or `company`
- Reuse existing agent logic from `recruitment_agent/agents/`

**Endpoints to create**:
1. `POST /api/recruitment/process-cvs/` - Process CV files
2. `GET /api/recruitment/job-descriptions/` - List job descriptions (filtered by company_user)
3. `POST /api/recruitment/job-descriptions/` - Create job description
4. `PUT /api/recruitment/job-descriptions/<id>/` - Update job description
5. `DELETE /api/recruitment/job-descriptions/<id>/` - Delete job description
6. `GET /api/recruitment/interviews/` - List interviews (filtered by company_user)
7. `POST /api/recruitment/interviews/schedule/` - Schedule interview
8. `GET /api/recruitment/interviews/<id>/` - Get interview details
9. `GET /api/recruitment/cv-records/` - List CV records (filtered by company_user)
10. `GET/POST /api/recruitment/settings/email/` - Email settings
11. `GET/POST /api/recruitment/settings/interview/` - Interview settings

### Task 2.2: Update Models for Company User Support
**Files**: `recruitment_agent/models.py`

- ✅ `JobDescription` already has `company_user` field
- ⚠️ `Interview` needs `company_user` field (currently only has `recruiter` User FK)
- ⚠️ `RecruiterEmailSettings` needs `company_user` field (currently only has `recruiter` User FK)
- ⚠️ `RecruiterInterviewSettings` needs `company_user` field (currently only has `recruiter` User FK)
- ✅ `CVRecord` can be filtered via `job_description__company_user`

**Migration needed**: Add `company_user` fields to `Interview`, `RecruiterEmailSettings`, `RecruiterInterviewSettings`

### Task 2.3: Update URL Routing
**File**: `api/urls.py`

Add recruitment agent routes:
```python
re_path(r'^recruitment/', include('api.views.recruitment_agent')),
```

---

## 3. Frontend Tasks

### Task 3.1: Create Recruitment Agent Service
**File**: `PaPerProjectFront/src/services/recruitmentAgentService.js` (new file)

Create service functions for all recruitment agent API calls:
- `processCVs(files, jobDescriptionId, options)`
- `getJobDescriptions()`
- `createJobDescription(data)`
- `updateJobDescription(id, data)`
- `deleteJobDescription(id)`
- `getInterviews(filters)`
- `scheduleInterview(data)`
- `getInterviewDetails(id)`
- `getCVRecords(filters)`
- `getEmailSettings()`
- `updateEmailSettings(data)`
- `getInterviewSettings()`
- `updateInterviewSettings(data)`

All should use `companyApi` from `companyAuthService.js` for authentication.

### Task 3.2: Add Recruitment Tab to Company Dashboard
**File**: `PaPerProjectFront/src/pages/CompanyDashboardPage.jsx`

- Add "Recruitment" tab to `TabsList`
- Add `TabsContent` for recruitment with routing to sub-components
- Similar structure to Projects tab

### Task 3.3: Create Recruitment Dashboard Component
**File**: `PaPerProjectFront/src/components/recruitment/RecruitmentDashboard.jsx` (new file)

Main dashboard showing:
- Statistics cards (total CVs processed, interviews scheduled, active jobs)
- Quick actions (Process CVs, Schedule Interview, Create Job)
- Recent activity feed

### Task 3.4: Create CV Processing Component
**File**: `PaPerProjectFront/src/components/recruitment/CVProcessing.jsx` (new file)

Features:
- File upload (multiple CV files)
- Job description selector
- Process button
- Results display:
  - Ranked candidates table
  - Role fit scores
  - Qualification decisions (INTERVIEW/HOLD/REJECT)
  - Candidate details modal
- Export results

### Task 3.5: Create Job Descriptions Management Component
**File**: `PaPerProjectFront/src/components/recruitment/JobDescriptions.jsx` (new file)

Features:
- List of job descriptions (table/cards)
- Create/Edit/Delete job descriptions
- Active/Inactive toggle
- Keywords display (from parsing)
- Link to CV processing with selected job

### Task 3.6: Create Interview Management Component
**File**: `PaPerProjectFront/src/components/recruitment/Interviews.jsx` (new file)

Features:
- List of interviews (filterable by status)
- Schedule new interview form
- Interview details view
- Status badges (PENDING, SCHEDULED, COMPLETED, CANCELLED)
- Calendar view (optional)
- Send reminder button

### Task 3.7: Create CV Records/Candidates Component
**File**: `PaPerProjectFront/src/components/recruitment/CVRecords.jsx` (new file)

Features:
- List of processed CVs
- Filtering (by job, qualification decision, date)
- Sorting (by rank, score, date)
- View candidate details
- Download parsed CV data
- Link to schedule interview

### Task 3.8: Create Recruiter Settings Component
**File**: `PaPerProjectFront/src/components/recruitment/RecruiterSettings.jsx` (new file)

Features:
- Email Settings:
  - Follow-up delay hours
  - Min hours between follow-ups
  - Max follow-up emails
  - Reminder hours before interview
  - Auto-send toggles
- Interview Settings:
  - Schedule date range
  - Daily time range
  - Interview time gap
  - Time slots preview

### Task 3.9: Style All Components
All components should:
- Use PayPerProject theme (same as CompanyDashboardPage)
- Use shadcn/ui components (Card, Button, Badge, Tabs, etc.)
- Match color scheme and typography
- Be responsive
- Include loading states and error handling

---

## 4. Data Flow

### 4.1 CV Processing Flow
1. User uploads CV files
2. User selects job description (or creates new)
3. Frontend calls `POST /api/recruitment/process-cvs/`
4. Backend:
   - Parses CVs using `CVParserAgent`
   - Summarizes using `SummarizationAgent`
   - Enriches using `LeadResearchEnrichmentAgent`
   - Qualifies using `LeadQualificationAgent`
   - Ranks candidates
   - Returns results
5. Frontend displays ranked candidates

### 4.2 Interview Scheduling Flow
1. User selects candidate from CV records
2. User clicks "Schedule Interview"
3. Frontend calls `POST /api/recruitment/interviews/schedule/`
4. Backend:
   - Creates interview with `InterviewSchedulingAgent`
   - Generates available slots
   - Sends invitation email
   - Returns interview details
5. Frontend shows interview details and confirmation

### 4.3 Job Description Flow
1. User creates/edits job description
2. Frontend calls `POST /api/recruitment/job-descriptions/` or `PUT /api/recruitment/job-descriptions/<id>/`
3. Backend:
   - Saves job description
   - Optionally parses keywords using `JobDescriptionParserAgent`
   - Links to `company_user`
4. Frontend refreshes job list

---

## 5. Implementation Priority

### Phase 1: Core Functionality (High Priority)
1. ✅ Backend API endpoints for company users
2. ✅ Model migrations for company_user fields
3. ✅ Frontend service layer
4. ✅ Job Descriptions management
5. ✅ CV Processing basic flow

### Phase 2: Interview Management (Medium Priority)
6. ✅ Interview scheduling
7. ✅ Interview list and details
8. ✅ CV Records list

### Phase 3: Settings & Polish (Lower Priority)
9. ✅ Recruiter settings
10. ✅ Statistics dashboard
11. ✅ Advanced filtering and search
12. ✅ Export functionality

---

## 6. Technical Considerations

### 6.1 Authentication
- All endpoints use `CompanyUserTokenAuthentication`
- Token passed in `Authorization: Token <token>` header
- Frontend uses `companyApi` helper (already configured)

### 6.2 Data Isolation
- All queries filter by `company_user` or `company`
- Company users only see their own data
- Similar pattern to Project Manager Agent

### 6.3 Error Handling
- Consistent error responses: `{status: 'error', message: '...'}`
- Frontend shows toast notifications for errors
- Loading states for async operations

### 6.4 File Uploads
- CV files uploaded as `multipart/form-data`
- Backend processes files using existing agent logic
- Frontend shows upload progress

---

## 7. Testing Checklist

- [ ] Company user can access recruitment tab
- [ ] Company user can create job descriptions
- [ ] Company user can process CVs
- [ ] Company user can view CV records
- [ ] Company user can schedule interviews
- [ ] Company user can view interviews
- [ ] Company user can update settings
- [ ] Data is properly filtered by company_user
- [ ] Authentication works correctly
- [ ] Error handling works
- [ ] UI matches PayPerProject theme

---

## 8. Files to Create/Modify

### Backend:
- `api/views/recruitment_agent.py` (NEW)
- `api/urls.py` (MODIFY - add routes)
- `recruitment_agent/models.py` (MODIFY - add company_user fields)
- `recruitment_agent/migrations/00XX_add_company_user_fields.py` (NEW)

### Frontend:
- `PaPerProjectFront/src/services/recruitmentAgentService.js` (NEW)
- `PaPerProjectFront/src/pages/CompanyDashboardPage.jsx` (MODIFY - add tab)
- `PaPerProjectFront/src/components/recruitment/RecruitmentDashboard.jsx` (NEW)
- `PaPerProjectFront/src/components/recruitment/CVProcessing.jsx` (NEW)
- `PaPerProjectFront/src/components/recruitment/JobDescriptions.jsx` (NEW)
- `PaPerProjectFront/src/components/recruitment/Interviews.jsx` (NEW)
- `PaPerProjectFront/src/components/recruitment/CVRecords.jsx` (NEW)
- `PaPerProjectFront/src/components/recruitment/RecruiterSettings.jsx` (NEW)

---

## 9. Next Steps

1. Review and approve this plan
2. Start with Phase 1 (Backend APIs)
3. Create model migrations
4. Build frontend service layer
5. Create UI components incrementally
6. Test each feature as it's built
7. Polish and optimize

---

**Last Updated**: 2026-01-19
**Status**: Planning Complete - Ready for Implementation


