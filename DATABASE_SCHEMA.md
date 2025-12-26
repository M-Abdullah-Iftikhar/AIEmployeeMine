# PayPerProject Database Schema Documentation

**Database Name:** `payPerProject`  
**Database Engine:** Microsoft SQL Server

---

## Table of Contents

- [Core User Tables](#core-user-tables)
- [Project Management Tables](#project-management-tables)
- [Company & Career Tables](#company--career-tables)
- [Financial Tables](#financial-tables)
- [Content & Communication Tables](#content--communication-tables)
- [Analytics & Tracking Tables](#analytics--tracking-tables)
- [System Tables](#system-tables)

---

## Core User Tables

### `ppp_users`
Main user table storing all user accounts.

**Fields:**
- `id` (bigint, PK, IDENTITY) - Primary key
- `email` (nvarchar(255), UNIQUE, NOT NULL) - User email address
- `password_hash` (nvarchar(255), NOT NULL) - Hashed password
- `first_name` (nvarchar(100), NULL)
- `last_name` (nvarchar(100), NULL)
- `phone` (nvarchar(20), NULL)
- `user_type` (nvarchar(50), NOT NULL) - Values: 'client', 'freelancer', 'admin', 'project_manager'
- `account_status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'active', 'inactive', 'suspended'
- `email_verified` (bit, NOT NULL, DEFAULT: 0)
- `last_login` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Referenced by: `ppp_user_profiles`, `ppp_user_sessions`, `ppp_user_verifications`, `ppp_user_activity_logs`, `ppp_analytics_events`, `ppp_chatbot_conversations`, `ppp_projects`, `ppp_project_team_members`, `ppp_project_applications`, `ppp_consultations`, `ppp_talent_requests`, `ppp_credits`, `ppp_subscriptions`, `ppp_invoices`, `ppp_payments`, `ppp_payment_methods`, `ppp_notifications`, `ppp_page_views`, `ppp_referral_codes`, `ppp_referrals`, `ppp_blog_posts`, `ppp_white_label_products`, `ppp_company_registration_tokens`

---

### `ppp_user_profiles`
Extended user profile information.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`) - One-to-one relationship
- `company_name` (nvarchar(255), NULL)
- `bio` (nvarchar(max), NULL)
- `avatar_url` (nvarchar(500), NULL)
- `location` (nvarchar(255), NULL)
- `timezone` (nvarchar(50), NULL)
- `website` (nvarchar(255), NULL)
- `linkedin` (nvarchar(255), NULL)
- `github` (nvarchar(255), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (CASCADE DELETE)

---

### `ppp_user_sessions`
User session management.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `session_token` (nvarchar(255), UNIQUE, NOT NULL)
- `ip_address` (nvarchar(45), NULL)
- `user_agent` (nvarchar(max), NULL)
- `expires_at` (datetime2(7), NOT NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (CASCADE DELETE)

---

### `ppp_user_verifications`
Email/phone verification tokens.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `token` (nvarchar(255), UNIQUE, NOT NULL)
- `type` (nvarchar(50), NOT NULL) - Values: 'email', 'phone', 'password_reset'
- `verified` (bit, NOT NULL, DEFAULT: 0)
- `expires_at` (datetime2(7), NOT NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (CASCADE DELETE)

---

### `ppp_user_activity_logs`
Activity tracking for users.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `action` (nvarchar(100), NOT NULL)
- `entity_type` (nvarchar(50), NULL)
- `entity_id` (bigint, NULL)
- `details` (nvarchar(max), NULL)
- `ip_address` (nvarchar(45), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (CASCADE DELETE)

---

## Project Management Tables

### `ppp_projects`
Main projects table.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `client_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `project_manager_id` (bigint, NULL, FK → `ppp_users.id`)
- `title` (nvarchar(255), NOT NULL)
- `description` (nvarchar(max), NOT NULL)
- `industry_id` (bigint, NULL, FK → `ppp_industries.id`)
- `project_type` (nvarchar(50), NOT NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'draft') - Values: 'draft', 'posted', 'in_progress', 'review', 'completed', 'cancelled'
- `budget_min` (decimal(10,2), NULL)
- `budget_max` (decimal(10,2), NULL)
- `deadline` (date, NULL)
- `priority` (nvarchar(50), NOT NULL, DEFAULT: 'medium') - Values: 'low', 'medium', 'high', 'urgent'
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Keys:
  - `client_id` → `ppp_users.id`
  - `project_manager_id` → `ppp_users.id` (SET NULL)
  - `industry_id` → `ppp_industries.id` (SET NULL)
- Referenced by: `ppp_project_team_members`, `ppp_project_applications`, `ppp_project_milestones`, `ppp_project_documents`, `ppp_reviews`

---

### `ppp_project_team_members`
Junction table for project team assignments.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `project_id` (bigint, NOT NULL, FK → `ppp_projects.id`)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `role` (nvarchar(50), NOT NULL)
- `assigned_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `removed_at` (datetime2(7), NULL)

**Relationships:**
- Foreign Keys:
  - `project_id` → `ppp_projects.id` (CASCADE DELETE)
  - `user_id` → `ppp_users.id`

---

### `ppp_project_applications`
Freelancer applications for projects.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `project_id` (bigint, NOT NULL, FK → `ppp_projects.id`)
- `freelancer_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `proposal` (nvarchar(max), NOT NULL)
- `estimated_cost` (decimal(10,2), NULL)
- `estimated_duration` (int, NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'shortlisted', 'accepted', 'rejected'
- `applied_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Keys:
  - `project_id` → `ppp_projects.id` (CASCADE DELETE)
  - `freelancer_id` → `ppp_users.id`

---

### `ppp_project_milestones`
Project milestone tracking.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `project_id` (bigint, NOT NULL, FK → `ppp_projects.id`)
- `title` (nvarchar(255), NOT NULL)
- `description` (nvarchar(max), NULL)
- `due_date` (date, NOT NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'in_progress', 'completed', 'cancelled'
- `completed_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `project_id` → `ppp_projects.id` (CASCADE DELETE)

---

### `ppp_project_documents`
Document storage for projects.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `project_id` (bigint, NOT NULL, FK → `ppp_projects.id`)
- `uploaded_by` (bigint, NOT NULL, FK → `ppp_users.id`)
- `file_name` (nvarchar(255), NOT NULL)
- `file_path` (nvarchar(500), NOT NULL)
- `file_type` (nvarchar(50), NOT NULL)
- `file_size` (bigint, NOT NULL)
- `document_type` (nvarchar(50), NOT NULL) - Values: 'requirement', 'deliverable', 'contract', 'other'
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Keys:
  - `project_id` → `ppp_projects.id` (CASCADE DELETE)
  - `uploaded_by` → `ppp_users.id`

---

### `ppp_industries`
Industry categories for projects.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `name` (nvarchar(255), NOT NULL)
- `slug` (nvarchar(255), UNIQUE, NOT NULL)
- `category` (nvarchar(100), NOT NULL)
- `description` (nvarchar(max), NOT NULL)
- `icon` (nvarchar(100), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Referenced by: `ppp_projects`, `ppp_industry_challenges`

---

### `ppp_industry_challenges`
Industry-specific challenges and solutions.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `industry_slug` (nvarchar(255), NOT NULL) - References `ppp_industries.slug`
- `challenge_title` (nvarchar(255), NOT NULL)
- `challenge_description` (nvarchar(max), NOT NULL)
- `solution` (nvarchar(max), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

---

## Company & Career Tables

### `ppp_companies`
Company/organization information.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `name` (nvarchar(255), NOT NULL)
- `email` (nvarchar(255), NOT NULL)
- `phone` (nvarchar(20), NULL)
- `address` (nvarchar(500), NULL)
- `website` (nvarchar(255), NULL)
- `industry` (nvarchar(100), NULL)
- `company_size` (nvarchar(50), NULL)
- `description` (nvarchar(max), NULL)
- `is_active` (bit, NOT NULL, DEFAULT: 1)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Referenced by: `ppp_company_users`, `ppp_company_registration_tokens`, `ppp_job_positions`, `ppp_career_applications`

---

### `ppp_company_users`
Users belonging to companies.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `company_id` (bigint, NOT NULL, FK → `ppp_companies.id`)
- `email` (nvarchar(255), NOT NULL) - Unique per company
- `password_hash` (nvarchar(255), NOT NULL)
- `full_name` (nvarchar(255), NOT NULL)
- `role` (nvarchar(50), NOT NULL, DEFAULT: 'admin') - Values: 'admin', 'manager', 'recruiter'
- `is_active` (bit, NOT NULL, DEFAULT: 1)
- `last_login` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `company_id` → `ppp_companies.id` (CASCADE DELETE)
- Unique Constraint: `(company_id, email)`

---

### `ppp_company_registration_tokens`
Registration tokens for company user invitations.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `token` (nvarchar(255), UNIQUE, NOT NULL)
- `company_id` (bigint, NULL, FK → `ppp_companies.id`)
- `expires_at` (datetime2(7), NOT NULL)
- `is_used` (bit, NOT NULL, DEFAULT: 0)
- `created_by` (bigint, NULL, FK → `ppp_users.id`)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `used_at` (datetime2(7), NULL)

**Relationships:**
- Foreign Keys:
  - `company_id` → `ppp_companies.id`
  - `created_by` → `ppp_users.id`

---

### `ppp_job_positions`
Job postings/positions.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `title` (nvarchar(255), NOT NULL)
- `location` (nvarchar(255), NOT NULL)
- `department` (nvarchar(255), NOT NULL)
- `type` (nvarchar(50), NOT NULL, DEFAULT: 'Full-time') - Values: 'Full-time', 'Part-time', 'Contract', 'Internship'
- `description` (nvarchar(max), NULL)
- `requirements` (nvarchar(max), NULL)
- `is_active` (bit, NOT NULL, DEFAULT: 1)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `company_id` (bigint, NULL, FK → `ppp_companies.id`)

**Relationships:**
- Foreign Key: `company_id` → `ppp_companies.id` (SET NULL)
- Referenced by: `ppp_career_applications`

---

### `ppp_career_applications`
Job applications.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `position_title` (nvarchar(255), NOT NULL)
- `applicant_name` (nvarchar(255), NOT NULL)
- `email` (nvarchar(255), NOT NULL)
- `phone` (nvarchar(20), NULL)
- `resume_path` (nvarchar(500), NULL)
- `cover_letter` (nvarchar(max), NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'reviewing', 'interview', 'accepted', 'rejected'
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `position_id` (bigint, NULL, FK → `ppp_job_positions.id`)
- `application_token` (nvarchar(255), UNIQUE, NULL)
- `company_id` (bigint, NULL, FK → `ppp_companies.id`)

**Relationships:**
- Foreign Keys:
  - `position_id` → `ppp_job_positions.id`
  - `company_id` → `ppp_companies.id` (SET NULL)

---

## Financial Tables

### `ppp_pricing_plans`
Subscription pricing plans.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `name` (nvarchar(50), UNIQUE, NOT NULL)
- `price` (decimal(10,2), NOT NULL)
- `currency` (nvarchar(3), NOT NULL, DEFAULT: 'GBP')
- `description` (nvarchar(max), NOT NULL)
- `features` (nvarchar(max), NOT NULL)
- `is_featured` (bit, NOT NULL, DEFAULT: 0)
- `is_active` (bit, NOT NULL, DEFAULT: 1)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Referenced by: `ppp_subscriptions`

---

### `ppp_subscriptions`
User subscriptions to pricing plans.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `plan_id` (bigint, NOT NULL, FK → `ppp_pricing_plans.id`)
- `status` (nvarchar(50), NOT NULL) - Values: 'active', 'cancelled', 'expired', 'trial'
- `started_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `expires_at` (datetime2(7), NULL)
- `cancelled_at` (datetime2(7), NULL)
- `auto_renew` (bit, NOT NULL, DEFAULT: 1)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Keys:
  - `user_id` → `ppp_users.id` (CASCADE DELETE)
  - `plan_id` → `ppp_pricing_plans.id`
- Referenced by: `ppp_invoices`

---

### `ppp_invoices`
Billing invoices.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `subscription_id` (bigint, NULL, FK → `ppp_subscriptions.id`)
- `invoice_number` (nvarchar(50), UNIQUE, NOT NULL)
- `amount` (decimal(10,2), NOT NULL)
- `currency` (nvarchar(3), NOT NULL, DEFAULT: 'GBP')
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'paid', 'overdue', 'cancelled'
- `due_date` (date, NOT NULL)
- `paid_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Keys:
  - `user_id` → `ppp_users.id`
  - `subscription_id` → `ppp_subscriptions.id` (SET NULL)
- Referenced by: `ppp_payments`

---

### `ppp_payments`
Payment transactions.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `invoice_id` (bigint, NULL, FK → `ppp_invoices.id`)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `amount` (decimal(10,2), NOT NULL)
- `currency` (nvarchar(3), NOT NULL, DEFAULT: 'GBP')
- `payment_method_id` (bigint, NULL, FK → `ppp_payment_methods.id`)
- `payment_gateway` (nvarchar(50), NOT NULL)
- `transaction_id` (nvarchar(255), UNIQUE, NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'completed', 'failed', 'refunded'
- `processed_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Keys:
  - `invoice_id` → `ppp_invoices.id` (SET NULL)
  - `user_id` → `ppp_users.id`
  - `payment_method_id` → `ppp_payment_methods.id` (SET NULL)

---

### `ppp_payment_methods`
Stored payment methods (credit cards, etc.).

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `type` (nvarchar(50), NOT NULL) - Values: 'credit_card', 'debit_card', 'bank_transfer', 'paypal', 'other'
- `gateway_customer_id` (nvarchar(255), NULL)
- `gateway_payment_method_id` (nvarchar(255), NULL)
- `last_four` (nvarchar(4), NULL)
- `brand` (nvarchar(50), NULL)
- `expiry_month` (tinyint, NULL)
- `expiry_year` (smallint, NULL)
- `is_default` (bit, NOT NULL, DEFAULT: 0)
- `is_active` (bit, NOT NULL, DEFAULT: 1)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (CASCADE DELETE)
- Referenced by: `ppp_payments`

---

### `ppp_credits`
User credit balance.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`, UNIQUE)
- `balance` (decimal(10,2), NOT NULL, DEFAULT: 0)
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (CASCADE DELETE)
- Referenced by: `ppp_credit_transactions`

---

### `ppp_credit_transactions`
Credit transaction history.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `credit_id` (bigint, NOT NULL, FK → `ppp_credits.id`)
- `amount` (decimal(10,2), NOT NULL)
- `type` (nvarchar(50), NOT NULL) - Values: 'earned', 'spent', 'refunded', 'expired'
- `description` (nvarchar(max), NULL)
- `reference_type` (nvarchar(50), NULL)
- `reference_id` (bigint, NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `credit_id` → `ppp_credits.id` (CASCADE DELETE)

---

### `ppp_referral_codes`
Referral code system.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `code` (nvarchar(50), UNIQUE, NOT NULL)
- `reward_type` (nvarchar(50), NOT NULL) - Values: 'credit', 'discount', 'cash'
- `reward_amount` (decimal(10,2), NOT NULL)
- `max_uses` (int, NULL)
- `current_uses` (int, NOT NULL, DEFAULT: 0)
- `expires_at` (datetime2(7), NULL)
- `is_active` (bit, NOT NULL, DEFAULT: 1)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (CASCADE DELETE)
- Referenced by: `ppp_referrals`

---

### `ppp_referrals`
Referral usage tracking.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `referral_code_id` (bigint, NOT NULL, FK → `ppp_referral_codes.id`)
- `referrer_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `referred_user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'completed', 'cancelled'
- `reward_earned` (decimal(10,2), NULL)
- `reward_paid_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Keys:
  - `referral_code_id` → `ppp_referral_codes.id` (CASCADE DELETE)
  - `referrer_id` → `ppp_users.id`
  - `referred_user_id` → `ppp_users.id`

---

## Content & Communication Tables

### `ppp_blog_posts`
Blog/article posts.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `slug` (nvarchar(255), UNIQUE, NOT NULL)
- `title` (nvarchar(255), NOT NULL)
- `description` (nvarchar(max), NOT NULL)
- `content` (nvarchar(max), NOT NULL)
- `author_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `category` (nvarchar(100), NOT NULL)
- `featured_image` (nvarchar(500), NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'draft') - Values: 'draft', 'published', 'archived'
- `published_at` (datetime2(7), NULL)
- `views_count` (int, NOT NULL, DEFAULT: 0)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `author_id` → `ppp_users.id` (CASCADE DELETE)
- Referenced by: `ppp_blog_post_tags`

---

### `ppp_blog_tags`
Blog post tags.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `name` (nvarchar(100), UNIQUE, NOT NULL)
- `slug` (nvarchar(100), UNIQUE, NOT NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Referenced by: `ppp_blog_post_tags`

---

### `ppp_blog_post_tags`
Junction table for blog posts and tags (many-to-many).

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `post_id` (bigint, NOT NULL, FK → `ppp_blog_posts.id`)
- `tag_id` (bigint, NOT NULL, FK → `ppp_blog_tags.id`)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Keys:
  - `post_id` → `ppp_blog_posts.id` (CASCADE DELETE)
  - `tag_id` → `ppp_blog_tags.id` (CASCADE DELETE)
- Unique Constraint: `(post_id, tag_id)`

---

### `ppp_faqs`
Frequently asked questions.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `question` (nvarchar(max), NOT NULL)
- `answer` (nvarchar(max), NOT NULL)
- `category` (nvarchar(100), NULL)
- `display_order` (int, NOT NULL, DEFAULT: 0)
- `is_active` (bit, NOT NULL, DEFAULT: 1)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

---

### `ppp_contact_messages`
Contact form submissions.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `full_name` (nvarchar(255), NOT NULL)
- `email` (nvarchar(255), NOT NULL)
- `phone` (nvarchar(20), NULL)
- `project_title` (nvarchar(255), NULL)
- `message` (nvarchar(max), NOT NULL)
- `attachment_path` (nvarchar(500), NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'new') - Values: 'new', 'read', 'replied', 'archived'
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

---

### `ppp_complaints`
Customer complaints.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `complaint_name` (nvarchar(255), NULL)
- `complaint_email` (nvarchar(255), NOT NULL)
- `complaint_message` (nvarchar(max), NOT NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'in_review', 'resolved', 'archived'
- `resolved_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

---

### `ppp_consultations`
Consultation requests.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `client_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `project_type` (nvarchar(100), NOT NULL)
- `requirements` (nvarchar(max), NOT NULL)
- `budget_range` (nvarchar(100), NULL)
- `timeline` (nvarchar(100), NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'scheduled', 'completed', 'cancelled'
- `scheduled_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `client_id` → `ppp_users.id` (CASCADE DELETE)

---

### `ppp_chatbot_conversations`
Chatbot conversation sessions.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NULL, FK → `ppp_users.id`)
- `session_id` (nvarchar(255), UNIQUE, NOT NULL)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'active') - Values: 'active', 'closed', 'archived'
- `started_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `ended_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (SET NULL)
- Referenced by: `ppp_chatbot_messages`

---

### `ppp_chatbot_messages`
Chatbot conversation messages.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `conversation_id` (bigint, NOT NULL, FK → `ppp_chatbot_conversations.id`)
- `sender_type` (nvarchar(50), NOT NULL) - Values: 'user', 'bot'
- `message` (nvarchar(max), NOT NULL)
- `metadata` (nvarchar(max), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `conversation_id` → `ppp_chatbot_conversations.id` (CASCADE DELETE)

---

### `ppp_reviews`
Customer reviews/testimonials.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `client_name` (nvarchar(255), NOT NULL)
- `company` (nvarchar(255), NOT NULL)
- `quote` (nvarchar(max), NOT NULL)
- `rating` (decimal(2,1), NOT NULL) - Range: 1.0 to 5.0
- `project_id` (bigint, NULL, FK → `ppp_projects.id`)
- `featured` (bit, NOT NULL, DEFAULT: 0)
- `date` (date, NOT NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `project_id` → `ppp_projects.id` (SET NULL)

---

### `ppp_talent_requests`
Talent/recruitment requests.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `client_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `title` (nvarchar(255), NOT NULL)
- `description` (nvarchar(max), NOT NULL)
- `skills_required` (nvarchar(max), NULL)
- `experience_level` (nvarchar(50), NULL) - Values: 'junior', 'mid', 'senior', 'expert'
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'pending') - Values: 'pending', 'in_progress', 'fulfilled', 'cancelled'
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `client_id` → `ppp_users.id` (CASCADE DELETE)

---

## Analytics & Tracking Tables

### `ppp_analytics_events`
Analytics event tracking.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NULL, FK → `ppp_users.id`)
- `event_type` (nvarchar(100), NOT NULL)
- `event_name` (nvarchar(255), NOT NULL)
- `properties` (nvarchar(max), NULL)
- `ip_address` (nvarchar(45), NULL)
- `user_agent` (nvarchar(max), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (SET NULL)

---

### `ppp_page_views`
Page view tracking.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NULL, FK → `ppp_users.id`)
- `page_path` (nvarchar(500), NOT NULL)
- `referrer` (nvarchar(500), NULL)
- `session_id` (nvarchar(255), NULL)
- `duration` (int, NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (SET NULL)

---

### `ppp_notifications`
User notifications.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `user_id` (bigint, NOT NULL, FK → `ppp_users.id`)
- `type` (nvarchar(50), NOT NULL)
- `title` (nvarchar(255), NOT NULL)
- `message` (nvarchar(max), NOT NULL)
- `link` (nvarchar(500), NULL)
- `is_read` (bit, NOT NULL, DEFAULT: 0)
- `read_at` (datetime2(7), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `user_id` → `ppp_users.id` (CASCADE DELETE)

---

## System Tables

### `ppp_ai_predictor_submissions`
AI project predictor submissions.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `email` (nvarchar(255), NOT NULL)
- `project_type` (nvarchar(100), NOT NULL)
- `project_data` (nvarchar(max), NOT NULL)
- `predicted_cost` (decimal(10,2), NULL)
- `predicted_duration` (int, NULL)
- `predicted_team_size` (int, NULL)
- `prediction_confidence` (decimal(5,2), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

---

### `ppp_quiz_responses`
Quiz/questionnaire responses.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `email` (nvarchar(255), NOT NULL)
- `name` (nvarchar(255), NULL)
- `location` (nvarchar(255), NULL)
- `industry` (nvarchar(100), NULL)
- `goal` (nvarchar(100), NULL)
- `project_type` (nvarchar(100), NULL)
- `responses` (nvarchar(max), NOT NULL)
- `recommendations` (nvarchar(max), NULL)
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

---

### `ppp_white_label_products`
White-label product catalog.

**Fields:**
- `id` (bigint, PK, IDENTITY)
- `name` (nvarchar(255), NOT NULL)
- `description` (nvarchar(max), NOT NULL)
- `category` (nvarchar(100), NOT NULL)
- `partner_id` (bigint, NULL, FK → `ppp_users.id`)
- `featured` (bit, NOT NULL, DEFAULT: 0)
- `status` (nvarchar(50), NOT NULL, DEFAULT: 'draft') - Values: 'draft', 'active', 'inactive'
- `created_at` (datetime2(7), NOT NULL, DEFAULT: getdate())
- `updated_at` (datetime2(7), NOT NULL, DEFAULT: getdate())

**Relationships:**
- Foreign Key: `partner_id` → `ppp_users.id` (SET NULL)

---

## Entity Relationship Summary

### Core Relationships

1. **Users → Multiple Tables**
   - Users can have: profiles, sessions, verifications, activity logs
   - Users can own: projects (as clients), subscriptions, invoices, payments, credits, referrals
   - Users can be assigned to: projects (as team members), project applications (as freelancers)

2. **Projects → Related Tables**
   - Projects belong to: clients (users), project managers (users), industries
   - Projects have: team members, applications, milestones, documents, reviews

3. **Financial Flow**
   - Users → Subscriptions → Invoices → Payments
   - Users → Credits → Credit Transactions
   - Users → Referral Codes → Referrals

4. **Company Structure**
   - Companies → Company Users
   - Companies → Job Positions → Career Applications
   - Companies → Company Registration Tokens

5. **Content Management**
   - Blog Posts → Blog Tags (many-to-many via `ppp_blog_post_tags`)
   - Blog Posts → Users (author)

### Key Junction Tables

- `ppp_project_team_members` - Links projects and users (team assignments)
- `ppp_project_applications` - Links projects and users (freelancer applications)
- `ppp_blog_post_tags` - Links blog posts and tags (many-to-many)
- `ppp_referrals` - Links referral codes, referrers, and referred users

---

## Notes

- All tables use `bigint` for primary keys with `IDENTITY(1,1)` auto-increment
- Timestamps use `datetime2(7)` for precision
- Many tables include `created_at` and `updated_at` fields with default values
- Foreign key constraints use CASCADE DELETE where appropriate to maintain referential integrity
- Status fields typically use CHECK constraints to limit valid values
- Several tables include unique constraints on email addresses, slugs, tokens, etc.
- Text fields use `nvarchar(max)` for variable-length content
- Decimal fields use `decimal(10,2)` for currency and `decimal(5,2)` or `decimal(2,1)` for percentages/ratings

