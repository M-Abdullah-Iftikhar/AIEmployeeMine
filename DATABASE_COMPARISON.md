# Database Schema Comparison: Django Project vs payPerProject Database

This document maps the tables from your Django project to the payPerProject database schema and identifies missing and extra fields.

---

## Table Mappings

### 1. User Model (`auth_user` in Django) ↔ `ppp_users`

**Django User Model (auth_user):**
- `id` (AutoField, PK)
- `username` (CharField, unique)
- `email` (EmailField, unique)
- `password` (CharField) - hashed
- `first_name` (CharField)
- `last_name` (CharField)
- `is_staff` (BooleanField)
- `is_active` (BooleanField)
- `is_superuser` (BooleanField)
- `date_joined` (DateTimeField)
- `last_login` (DateTimeField)

**payPerProject `ppp_users`:**
- `id` (bigint, PK)
- `email` (nvarchar(255), UNIQUE, NOT NULL) ✅
- `password_hash` (nvarchar(255), NOT NULL) ✅ (equivalent to password)
- `first_name` (nvarchar(100), NULL) ✅
- `last_name` (nvarchar(100), NULL) ✅
- `phone` (nvarchar(20), NULL)
- `user_type` (nvarchar(50), NOT NULL) - Values: 'client', 'freelancer', 'admin', 'project_manager'
- `account_status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'active', 'inactive', 'suspended'
- `email_verified` (bit, NOT NULL, DEFAULT: 0)
- `last_login` (datetime2(7), NULL) ✅
- `created_at` (datetime2(7), NOT NULL) ✅ (equivalent to date_joined)
- `updated_at` (datetime2(7), NOT NULL)

#### Missing in Django User Model:
- ❌ `phone` - Phone number field
- ❌ `user_type` - Explicit user type (client, freelancer, admin, project_manager)
- ❌ `account_status` - Account status tracking (pending, active, inactive, suspended)
- ❌ `email_verified` - Email verification status
- ❌ `updated_at` - Last update timestamp

#### Extra in Django User Model:
- ✅ `username` - Django uses username, payPerProject uses email as primary identifier
- ✅ `is_staff` - Staff status flag
- ✅ `is_superuser` - Superuser status flag
- ✅ `date_joined` - (Similar to created_at, but different name)

---

### 2. UserProfile (`core_userprofile`) ↔ `ppp_user_profiles`

**Django UserProfile:**
- `id` (AutoField, PK)
- `user` (OneToOneField → User)
- `role` (CharField) - Values: 'project_manager', 'team_member', 'developer', 'viewer', 'recruitment_agent', 'marketing_agent'
- `created_at` (DateTimeField) ✅
- `updated_at` (DateTimeField) ✅

**payPerProject `ppp_user_profiles`:**
- `id` (bigint, PK)
- `user_id` (bigint, FK → ppp_users.id) ✅
- `company_name` (nvarchar(255), NULL)
- `bio` (nvarchar(max), NULL)
- `avatar_url` (nvarchar(500), NULL)
- `location` (nvarchar(255), NULL)
- `timezone` (nvarchar(50), NULL)
- `website` (nvarchar(255), NULL)
- `linkedin` (nvarchar(255), NULL)
- `github` (nvarchar(255), NULL)
- `created_at` (datetime2(7), NOT NULL) ✅
- `updated_at` (datetime2(7), NOT NULL) ✅

#### Missing in Django UserProfile:
- ❌ `company_name` - Company/organization name
- ❌ `bio` - User biography/description
- ❌ `avatar_url` - Profile picture URL
- ❌ `location` - User location
- ❌ `timezone` - Timezone information
- ❌ `website` - Personal/professional website
- ❌ `linkedin` - LinkedIn profile URL
- ❌ `github` - GitHub profile URL

#### Extra in Django UserProfile:
- ✅ `role` - Role field exists in Django but not in payPerProject user_profiles (note: role is in ppp_users as user_type)

---

### 3. Project (`core_project`) ↔ `ppp_projects`

**Django Project:**
- `id` (AutoField, PK)
- `name` (CharField, max_length=200) ✅
- `description` (TextField) ✅
- `owner` (ForeignKey → User) ✅ (maps to client_id)
- `status` (CharField) - Values: 'planning', 'active', 'on_hold', 'completed', 'cancelled'
- `priority` (CharField) - Values: 'low', 'medium', 'high' ✅
- `start_date` (DateField, nullable) ✅
- `end_date` (DateField, nullable) ✅
- `created_at` (DateTimeField) ✅
- `updated_at` (DateTimeField) ✅

**payPerProject `ppp_projects`:**
- `id` (bigint, PK)
- `client_id` (bigint, FK → ppp_users.id) ✅ (maps to owner)
- `project_manager_id` (bigint, NULL, FK → ppp_users.id)
- `title` (nvarchar(255), NOT NULL) ✅ (maps to name)
- `description` (nvarchar(max), NOT NULL) ✅
- `industry_id` (bigint, NULL, FK → ppp_industries.id)
- `project_type` (nvarchar(50), NOT NULL)
- `status` (nvarchar(50), NOT NULL) - Values: 'draft', 'posted', 'in_progress', 'review', 'completed', 'cancelled'
- `budget_min` (decimal(10,2), NULL)
- `budget_max` (decimal(10,2), NULL)
- `deadline` (date, NULL) ✅ (similar to end_date)
- `priority` (nvarchar(50), NOT NULL) - Values: 'low', 'medium', 'high', 'urgent' ✅
- `created_at` (datetime2(7), NOT NULL) ✅
- `updated_at` (datetime2(7), NOT NULL) ✅

#### Missing in Django Project:
- ❌ `project_manager_id` - Dedicated project manager assignment
- ❌ `industry_id` - Industry categorization
- ❌ `project_type` - Type of project (website, mobile_app, web_app, etc.)
- ❌ `budget_min` - Minimum budget
- ❌ `budget_max` - Maximum budget
- ❌ `deadline` - Project deadline (you have end_date, but deadline might be different concept)

#### Extra in Django Project:
- ✅ `start_date` - Explicit start date (payPerProject doesn't have this)
- ✅ `name` - (payPerProject uses 'title' instead)

#### Status Value Mapping:
- Django: 'planning', 'active', 'on_hold', 'completed', 'cancelled'
- payPerProject: 'draft', 'posted', 'in_progress', 'review', 'completed', 'cancelled'
- ⚠️ **Status values don't match exactly** - consider alignment

---

### 4. Task (`core_task`) ↔ No Direct Mapping

**Django Task:**
- `id` (AutoField, PK)
- `title` (CharField, max_length=200)
- `description` (TextField)
- `project` (ForeignKey → Project)
- `assignee` (ForeignKey → User, nullable)
- `status` (CharField) - Values: 'todo', 'in_progress', 'review', 'done', 'blocked'
- `priority` (CharField) - Values: 'low', 'medium', 'high'
- `due_date` (DateTimeField, nullable)
- `estimated_hours` (FloatField, nullable)
- `actual_hours` (FloatField, nullable)
- `progress_percentage` (IntegerField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)
- `completed_at` (DateTimeField, nullable)
- `depends_on` (ManyToManyField → self)

**Possible payPerProject Equivalent: `ppp_project_milestones`**

**payPerProject `ppp_project_milestones`:**
- `id` (bigint, PK)
- `project_id` (bigint, FK → ppp_projects.id) ✅
- `title` (nvarchar(255), NOT NULL) ✅
- `description` (nvarchar(max), NULL) ✅
- `due_date` (date, NOT NULL) ✅
- `status` (nvarchar(50), NOT NULL) - Values: 'pending', 'in_progress', 'completed', 'cancelled' ✅
- `completed_at` (datetime2(7), NULL) ✅
- `created_at` (datetime2(7), NOT NULL) ✅

#### Missing in payPerProject `ppp_project_milestones`:
- ❌ `assignee` - No assignee field (tasks are assigned to users, milestones are project-level)
- ❌ `estimated_hours` - No time estimation
- ❌ `actual_hours` - No actual hours tracking
- ❌ `progress_percentage` - No progress percentage
- ❌ `depends_on` - No dependency tracking
- ❌ `priority` - No priority field
- ❌ `updated_at` - No update timestamp

#### Extra in Django Task:
- ✅ `assignee` - Individual task assignment
- ✅ `estimated_hours` / `actual_hours` - Time tracking
- ✅ `progress_percentage` - Progress tracking
- ✅ `depends_on` - Task dependencies
- ✅ `priority` - Task priority
- ✅ `updated_at` - Update timestamp

**Note:** Tasks and Milestones serve different purposes:
- **Tasks** are detailed, assignable work items
- **Milestones** are project-level checkpoints

---

### 5. TeamMember (`core_teammember`) ↔ `ppp_project_team_members`

**Django TeamMember:**
- `id` (AutoField, PK)
- `user` (ForeignKey → User) ✅
- `project` (ForeignKey → Project) ✅
- `role` (CharField) - Values: 'owner', 'manager', 'member', 'viewer'
- `joined_at` (DateTimeField) ✅ (similar to assigned_at)

**payPerProject `ppp_project_team_members`:**
- `id` (bigint, PK)
- `project_id` (bigint, FK → ppp_projects.id) ✅
- `user_id` (bigint, FK → ppp_users.id) ✅
- `role` (nvarchar(50), NOT NULL) ✅
- `assigned_at` (datetime2(7), NOT NULL) ✅
- `removed_at` (datetime2(7), NULL)

#### Missing in Django TeamMember:
- ❌ `removed_at` - No tracking of when a team member was removed

#### Extra in Django TeamMember:
- None

**Note:** Role values differ:
- Django: 'owner', 'manager', 'member', 'viewer'
- payPerProject: Generic role field (exact values not specified in schema)

---

### 6. Subtask (`core_subtask`) ↔ No Direct Mapping

**Django Subtask:**
- `id` (AutoField, PK)
- `title` (CharField, max_length=300)
- `description` (TextField)
- `task` (ForeignKey → Task)
- `status` (CharField) - Values: 'todo', 'in_progress', 'done'
- `order` (IntegerField)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)
- `completed_at` (DateTimeField, nullable)

**payPerProject Equivalent:** None - No subtask table exists

**Missing in payPerProject:**
- ❌ Entire subtask concept is not present in payPerProject database

---

### 7. JobDescription (`recruitment_agent_jobdescription`) ↔ `ppp_job_positions`

**Django JobDescription:**
- `id` (AutoField, PK)
- `title` (CharField, max_length=255) ✅
- `description` (TextField) ✅
- `keywords_json` (TextField, nullable)
- `created_by` (ForeignKey → User, nullable) ✅
- `is_active` (BooleanField, default=True) ✅
- `created_at` (DateTimeField) ✅
- `updated_at` (DateTimeField) ✅

**payPerProject `ppp_job_positions`:**
- `id` (bigint, PK)
- `title` (nvarchar(255), NOT NULL) ✅
- `location` (nvarchar(255), NOT NULL)
- `department` (nvarchar(255), NOT NULL)
- `type` (nvarchar(50), NOT NULL) - Values: 'Full-time', 'Part-time', 'Contract', 'Internship'
- `description` (nvarchar(max), NULL) ✅
- `requirements` (nvarchar(max), NULL)
- `is_active` (bit, NOT NULL, DEFAULT: 1) ✅
- `created_at` (datetime2(7), NOT NULL) ✅
- `updated_at` (datetime2(7), NOT NULL) ✅
- `company_id` (bigint, NULL, FK → ppp_companies.id)

#### Missing in Django JobDescription:
- ❌ `location` - Job location
- ❌ `department` - Department/organizational unit
- ❌ `type` - Employment type (Full-time, Part-time, Contract, Internship)
- ❌ `requirements` - Job requirements (separate from description)
- ❌ `company_id` - Link to company (Django has created_by user, but no company)

#### Extra in Django JobDescription:
- ✅ `keywords_json` - Parsed keywords from AI analysis

---

### 8. CVRecord (`recruitment_agent_cvrecord`) ↔ No Direct Mapping in Schema Doc

**Django CVRecord:**
- `id` (AutoField, PK)
- `file_name` (CharField, max_length=512)
- `parsed_json` (TextField)
- `insights_json` (TextField, nullable)
- `role_fit_score` (IntegerField, nullable)
- `rank` (IntegerField, nullable)
- `enriched_json` (TextField, nullable)
- `qualification_json` (TextField, nullable)
- `qualification_decision` (CharField, max_length=32, nullable)
- `qualification_confidence` (IntegerField, nullable)
- `qualification_priority` (CharField, max_length=16, nullable)
- `job_description` (ForeignKey → JobDescription, nullable)
- `created_at` (DateTimeField)

**Note:** The Django model has `db_table = 'ppp_cv_records'`, suggesting it maps to a table in payPerProject database, but this table is not documented in the schema provided. This might be in a different database or the schema documentation is incomplete.

**Possible payPerProject Equivalent:** Might exist as `ppp_cv_records` (not in provided schema)

---

### 9. Interview (`recruitment_agent_interview`) ↔ Possible Mapping to `ppp_consultations` or `ppp_career_applications`

**Django Interview:**
- `id` (AutoField, PK)
- `candidate_name` (CharField, max_length=255)
- `candidate_email` (EmailField)
- `candidate_phone` (CharField, max_length=50, nullable)
- `job_role` (CharField, max_length=255)
- `interview_type` (CharField) - Values: 'ONLINE', 'ONSITE'
- `status` (CharField) - Values: 'PENDING', 'SCHEDULED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED'
- `scheduled_datetime` (DateTimeField, nullable)
- `selected_slot` (CharField, max_length=255, nullable)
- `available_slots_json` (TextField)
- `confirmation_token` (CharField, max_length=64, unique, nullable)
- `cv_record` (ForeignKey → CVRecord, nullable)
- `recruiter` (ForeignKey → User, nullable)
- `invitation_sent_at` (DateTimeField, nullable)
- `confirmation_sent_at` (DateTimeField, nullable)
- `last_reminder_sent_at` (DateTimeField, nullable)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)
- `notes` (TextField, nullable)

**payPerProject `ppp_consultations`:**
- `id` (bigint, PK)
- `client_id` (bigint, FK → ppp_users.id)
- `project_type` (nvarchar(100), NOT NULL)
- `requirements` (nvarchar(max), NOT NULL)
- `budget_range` (nvarchar(100), NULL)
- `timeline` (nvarchar(100), NULL)
- `status` (nvarchar(50), NOT NULL) - Values: 'pending', 'scheduled', 'completed', 'cancelled'
- `scheduled_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL)

**payPerProject `ppp_career_applications`:**
- `id` (bigint, PK)
- `position_title` (nvarchar(255), NOT NULL)
- `applicant_name` (nvarchar(255), NOT NULL)
- `email` (nvarchar(255), NOT NULL)
- `phone` (nvarchar(20), NULL)
- `resume_path` (nvarchar(500), NULL)
- `cover_letter` (nvarchar(max), NULL)
- `status` (nvarchar(50), NOT NULL) - Values: 'pending', 'reviewing', 'interview', 'accepted', 'rejected'
- `created_at` (datetime2(7), NOT NULL)
- `position_id` (bigint, NULL, FK → ppp_job_positions.id)
- `application_token` (nvarchar(255), UNIQUE, NULL)
- `company_id` (bigint, NULL, FK → ppp_companies.id)

#### Missing in payPerProject:
- ❌ No dedicated interview scheduling table exists
- Interview functionality would need to be added

#### Extra in Django Interview:
- ✅ Detailed interview scheduling (slots, tokens, reminders)
- ✅ Link to CV records
- ✅ Recruiter assignment
- ✅ Interview type tracking

**Note:** Interview is a Django-specific feature not present in payPerProject schema.

---

### 10. Meeting (`core_meeting`) ↔ No Direct Mapping

**Django Meeting:**
- `id` (AutoField, PK)
- `title` (CharField, max_length=200)
- `description` (TextField)
- `project` (ForeignKey → Project, nullable)
- `organizer` (ForeignKey → User)
- `participants` (ManyToManyField → User)
- `scheduled_at` (DateTimeField)
- `duration_minutes` (IntegerField)
- `notes` (TextField)
- `transcript` (TextField)
- `created_at` (DateTimeField)

**payPerProject Equivalent:** None - No meeting table exists

**Missing in payPerProject:**
- ❌ Entire meeting management feature is not present

---

### 11. ActionItem (`core_actionitem`) ↔ No Direct Mapping

**Django ActionItem:**
- `id` (AutoField, PK)
- `title` (CharField, max_length=200)
- `description` (TextField)
- `meeting` (ForeignKey → Meeting, nullable)
- `task` (ForeignKey → Task, nullable)
- `assignee` (ForeignKey → User, nullable)
- `due_date` (DateTimeField, nullable)
- `status` (CharField) - Values: 'open', 'in_progress', 'completed', 'cancelled'
- `created_at` (DateTimeField)
- `completed_at` (DateTimeField, nullable)

**payPerProject Equivalent:** None - No action item table exists

---

### 12. Workflow (`core_workflow`) ↔ No Direct Mapping

**Django Workflow:**
- `id` (AutoField, PK)
- `name` (CharField, max_length=200)
- `description` (TextField)
- `project` (ForeignKey → Project, nullable)
- `is_template` (BooleanField)
- `created_by` (ForeignKey → User)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**payPerProject Equivalent:** None - No workflow/SOP table exists

---

### 13. WorkflowStep (`core_workflowstep`) ↔ No Direct Mapping

**Django WorkflowStep:**
- `id` (AutoField, PK)
- `workflow` (ForeignKey → Workflow)
- `step_number` (IntegerField)
- `title` (CharField, max_length=200)
- `description` (TextField)
- `is_required` (BooleanField)
- `estimated_time_minutes` (IntegerField, nullable)

**payPerProject Equivalent:** None

---

### 14. WorkflowExecution (`core_workflowexecution`) ↔ No Direct Mapping

**Django WorkflowExecution:**
- `id` (AutoField, PK)
- `workflow` (ForeignKey → Workflow)
- `executed_by` (ForeignKey → User)
- `status` (CharField) - Values: 'pending', 'in_progress', 'completed', 'failed'
- `started_at` (DateTimeField)
- `completed_at` (DateTimeField, nullable)
- `context_data` (JSONField)

**payPerProject Equivalent:** None

---

### 15. Analytics (`core_analytics`) ↔ `ppp_analytics_events` (Partial)

**Django Analytics:**
- `id` (AutoField, PK)
- `project` (ForeignKey → Project)
- `metric_name` (CharField, max_length=100)
- `metric_value` (FloatField)
- `metric_data` (JSONField)
- `calculated_at` (DateTimeField)

**payPerProject `ppp_analytics_events`:**
- `id` (bigint, PK)
- `user_id` (bigint, NULL, FK → ppp_users.id)
- `event_type` (nvarchar(100), NOT NULL)
- `event_name` (nvarchar(255), NOT NULL)
- `properties` (nvarchar(max), NULL)
- `ip_address` (nvarchar(45), NULL)
- `user_agent` (nvarchar(max), NULL)
- `created_at` (datetime2(7), NOT NULL)

#### Missing in Django Analytics:
- ❌ `user_id` - No user tracking (only project-level)
- ❌ `event_type` - No event categorization
- ❌ `event_name` - No event naming
- ❌ `properties` - No flexible properties JSON
- ❌ `ip_address` / `user_agent` - No request metadata

#### Extra in Django Analytics:
- ✅ `project` - Direct project linkage
- ✅ `metric_value` - Numeric metric value
- ✅ `metric_data` - Structured metric data

**Note:** These serve different purposes:
- Django Analytics: Project-specific metrics
- payPerProject Analytics: User event tracking

---

### 16. Campaign (`marketing_agent_campaign`) ↔ No Direct Mapping

**Django Campaign:**
- `id` (AutoField, PK)
- `name` (CharField, max_length=200)
- `description` (TextField)
- `campaign_type` (CharField) - Values: 'email', 'social', 'paid', 'partnership', 'integrated'
- `status` (CharField) - Values: 'draft', 'scheduled', 'active', 'paused', 'completed', 'cancelled'
- `start_date` (DateField, nullable)
- `end_date` (DateField, nullable)
- `budget` (DecimalField)
- `actual_spend` (DecimalField)
- `target_audience` (JSONField)
- `goals` (JSONField)
- `channels` (JSONField)
- `owner` (ForeignKey → User)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**payPerProject Equivalent:** None - Marketing campaigns not present

---

### 17. MarketResearch (`marketing_agent_marketresearch`) ↔ No Direct Mapping

**Django MarketResearch:**
- `id` (AutoField, PK)
- `research_type` (CharField)
- `topic` (CharField, max_length=200)
- `findings` (JSONField)
- `insights` (TextField)
- `source_urls` (JSONField)
- `created_by` (ForeignKey → User)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**payPerProject Equivalent:** None - Market research not present

---

### 18. CampaignPerformance (`marketing_agent_campaignperformance`) ↔ No Direct Mapping

**Django CampaignPerformance:**
- `id` (AutoField, PK)
- `campaign` (ForeignKey → Campaign)
- `metric_name` (CharField)
- `metric_value` (DecimalField)
- `date` (DateField)
- `channel` (CharField, max_length=50)
- `target_value` (DecimalField, nullable)
- `actual_value` (DecimalField, nullable)
- `created_at` (DateTimeField)

**payPerProject Equivalent:** None

---

### 19. MarketingDocument (`marketing_agent_marketingdocument`) ↔ No Direct Mapping

**Django MarketingDocument:**
- `id` (AutoField, PK)
- `document_type` (CharField)
- `title` (CharField, max_length=200)
- `content` (TextField)
- `file_path` (CharField, max_length=500)
- `status` (CharField)
- `campaign` (ForeignKey → Campaign, nullable)
- `created_by` (ForeignKey → User)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**payPerProject Equivalent:** None - But might relate to `ppp_project_documents`

---

### 20. NotificationRule (`marketing_agent_notificationrule`) ↔ No Direct Mapping

**Django NotificationRule:**
- `id` (AutoField, PK)
- `rule_type` (CharField)
- `name` (CharField, max_length=200)
- `trigger_condition` (JSONField)
- `threshold_value` (DecimalField, nullable)
- `notification_message` (TextField)
- `is_active` (BooleanField)
- `campaign` (ForeignKey → Campaign, nullable)
- `created_by` (ForeignKey → User, nullable)
- `created_at` (DateTimeField)
- `last_triggered` (DateTimeField, nullable)

**payPerProject Equivalent:** None

---

## Tables in payPerProject NOT in Django Project

### Financial Tables (Complete Set Missing)
1. **ppp_pricing_plans** - Subscription pricing plans
2. **ppp_subscriptions** - User subscriptions
3. **ppp_invoices** - Billing invoices
4. **ppp_payments** - Payment transactions
5. **ppp_payment_methods** - Stored payment methods
6. **ppp_credits** - User credit balance
7. **ppp_credit_transactions** - Credit transaction history
8. **ppp_referral_codes** - Referral code system
9. **ppp_referrals** - Referral usage tracking

### Content Management
10. **ppp_blog_posts** - Blog/article posts
11. **ppp_blog_tags** - Blog post tags
12. **ppp_blog_post_tags** - Blog post-tag junction
13. **ppp_faqs** - Frequently asked questions
14. **ppp_reviews** - Customer reviews/testimonials

### Communication
15. **ppp_contact_messages** - Contact form submissions
16. **ppp_complaints** - Customer complaints
17. **ppp_consultations** - Consultation requests
18. **ppp_chatbot_conversations** - Chatbot conversation sessions
19. **ppp_chatbot_messages** - Chatbot conversation messages

### Company & Career (Partial)
20. **ppp_companies** - Company/organization information
21. **ppp_company_users** - Users belonging to companies
22. **ppp_company_registration_tokens** - Registration tokens
23. **ppp_career_applications** - Job applications (you have Interview, but not applications)

### Project Management (Additional)
24. **ppp_project_applications** - Freelancer applications for projects
25. **ppp_project_milestones** - Project milestone tracking (you have Tasks instead)
26. **ppp_project_documents** - Document storage for projects
27. **ppp_industries** - Industry categories
28. **ppp_industry_challenges** - Industry challenges

### User Management (Additional)
29. **ppp_user_sessions** - User session management
30. **ppp_user_verifications** - Email/phone verification tokens
31. **ppp_user_activity_logs** - Activity tracking

### Analytics & Tracking
32. **ppp_page_views** - Page view tracking
33. **ppp_notifications** - User notifications

### System Tables
34. **ppp_ai_predictor_submissions** - AI project predictor
35. **ppp_quiz_responses** - Quiz/questionnaire responses
36. **ppp_talent_requests** - Talent/recruitment requests
37. **ppp_white_label_products** - White-label product catalog

---

## Summary Statistics

- **Django Project Tables:** ~20 models
- **payPerProject Tables:** 43 tables
- **Mapped Tables:** 6 core mappings (User, UserProfile, Project, TeamMember, JobDescription, Analytics)
- **Django-Specific Tables:** 14 tables (Tasks, Subtasks, Meetings, ActionItems, Workflows, Marketing tables, etc.)
- **payPerProject-Specific Tables:** 37 tables (Financial, Content, Communication, Company management, etc.)

---

## Key Differences

1. **Architecture Focus:**
   - **Django Project:** Project management + AI agents (recruitment, marketing)
   - **payPerProject:** Full marketplace platform (projects + freelancers + payments + content)

2. **Financial System:**
   - payPerProject has complete financial infrastructure (subscriptions, payments, credits, referrals)
   - Django project has no financial tables

3. **Content Management:**
   - payPerProject has blog, FAQs, reviews, contact forms
   - Django project has none

4. **Task Management:**
   - Django has detailed Tasks + Subtasks with dependencies
   - payPerProject has Milestones (higher-level checkpoints)

5. **Company Management:**
   - payPerProject has multi-company support with company users
   - Django project has single-tenant user model

6. **User Model:**
   - Django uses username-based authentication
   - payPerProject uses email-based authentication with explicit user types

---

## Recommendations

### High Priority Fields to Add:

1. **User Model:**
   - Add `phone` field
   - Add `user_type` field (or map to UserProfile.role)
   - Add `account_status` field
   - Add `email_verified` field

2. **UserProfile:**
   - Add `company_name`, `bio`, `avatar_url`, `location`, `timezone`, `website`, `linkedin`, `github`

3. **Project:**
   - Add `project_manager_id` foreign key
   - Add `industry_id` foreign key
   - Add `project_type` field
   - Add `budget_min` and `budget_max` fields
   - Consider aligning status values

4. **JobDescription:**
   - Add `location`, `department`, `type`, `requirements` fields
   - Consider adding `company_id` foreign key

### Medium Priority:

5. Create `ProjectMilestone` model (separate from Task)
6. Create `ProjectDocument` model
7. Create `Industry` model
8. Consider adding `ProjectApplication` model for freelancer applications

### Low Priority (Django-Specific Features to Keep):

- Keep Tasks/Subtasks (more detailed than milestones)
- Keep Meetings, ActionItems (workflow features)
- Keep Workflows (SOP management)
- Keep Marketing models (campaign management)

---

**Generated:** Based on comparison between Django project models and payPerProject database schema documentation.

