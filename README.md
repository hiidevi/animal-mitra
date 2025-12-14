# Animal Mitra - Connecting Animal Helpers in Faridabad

#### Video Demo: [WILL ADD YOUTUBE URL AFTER RECORDING]

#### Live Demo: https://animalmitra.onrender.com

#### GitHub: [your-github-username]

#### edX Username: [your-edx-username]

#### Location: Faridabad, India

#### Date: December 14, 2025

---

## Description

Animal Mitra is a comprehensive web platform that connects animal lovers, individual volunteers, and animal welfare NGOs in Faridabad, India. The platform addresses the critical problem of coordinating help for street animals by creating a centralized directory of verified helpers and organizations.

### The Problem

India has one of the world's largest populations of street animals - millions of dogs, cats, cows, and birds living on the streets without proper care. When citizens encounter injured, sick, or hungry animals, they often don't know who to contact for immediate help. Similarly, individual volunteers and NGOs working to help animals operate independently without visibility, making it difficult for people to find them during emergencies.

### The Solution

Animal Mitra solves this coordination problem by providing:
- A searchable directory of individual animal helpers filtered by location and animal type
- A listing of verified NGOs with 24/7 emergency services
- A dual registration system for volunteers and organizations
- An admin verification workflow to ensure quality and prevent spam
- Contact information (phone, WhatsApp, Instagram) for immediate communication
- User dashboards showing impact metrics (profile views, calls received)

---

## Key Features

### 1. Helper Directory
Users can browse individual volunteers who dedicate their time to helping street animals. Each helper profile includes:
- Full name and specific location (Faridabad sectors)
- Types of animals they help (dogs, cats, cows, birds)
- Bio describing their experience and availability
- Contact information (mobile, WhatsApp, Instagram)
- Statistics (profile views, calls received)
- Search functionality by name or location
- Filter by animal type for quick finding

### 2. NGO Listings
For emergency situations requiring professional veterinary care or rescue services, the platform lists registered animal welfare NGOs with:
- Organization name and registration details
- 24/7 availability status with visual badges
- Comprehensive list of services (emergency rescue, veterinary care, shelter, sterilization, adoption)
- Operating hours and capacity information
- Verified status badges for authenticity
- Multiple contact methods for emergencies
- Detailed descriptions of facilities and expertise

### 3. Dual User Registration System
The platform supports two distinct user types with different registration flows:

**Individual Helpers:**
- Register with name, email, mobile number
- Select location (specific Faridabad sectors)
- Choose animals they help (multiple selection)
- Add bio and social media links
- Receive personalized dashboard showing profile views and contact statistics

**NGOs (Non-Governmental Organizations):**
- Register with organization name and registration number
- Provide establishment year and total capacity
- Mark 24/7 emergency availability
- Select multiple services offered
- Add operating hours and detailed address
- Get dedicated dashboard with organizational metrics

### 4. Admin Verification System
To ensure quality, safety, and prevent spam or fake listings:
- All new registrations receive "Pending" status
- Custom admin panel shows all pending users in one view
- Admins can review profile details, contact information
- One-click "Verify" or "Reject" actions
- Only verified users appear in public helper/NGO listings
- Verified badge displays prominently on profiles
- Email notifications for status changes (implemented via Django signals)

### 5. User Dashboards
Each user type receives a customized dashboard showing relevant metrics:

**Individual Dashboard:**
- Total profile views (how many people viewed their profile)
- Total calls received (engagement metric)
- Time active on platform (account age)
- Complete profile information with edit capability
- Verification status badge

**NGO Dashboard:**
- Profile views counter
- Emergency calls received
- Total capacity information
- Service statistics
- Verification status

### 6. Responsive Mobile-First Design
Recognizing that most Indian internet users browse on smartphones:
- Fully responsive design using Bootstrap 5 grid system
- Mobile-optimized cards and navigation
- Touch-friendly buttons (minimum 44px height)
- Collapsible navbar for mobile
- Optimized images and fast loading
- Tested on iOS and Android devices

---

## Technical Implementation

### Technology Stack

**Backend Framework:**
- Django 5.0.1 (Python web framework)
- Django ORM for database operations
- Django authentication system (customized)
- Django admin interface (customized)

**Database:**
- SQLite for local development (zero configuration)
- PostgreSQL for production on Render
- Database switching via environment variables

**Frontend:**
- Bootstrap 5.3 (responsive CSS framework)
- Bootstrap Icons library
- Custom CSS for brand colors (#9ACD32 green theme)
- Vanilla JavaScript (no heavy frameworks)

**Deployment & Infrastructure:**
- Render web service (free tier)
- PostgreSQL database on Render
- Gunicorn WSGI server
- WhiteNoise for static file serving
- Environment variables via python-decouple

**Email Service:**
- Gmail SMTP for development
- Resend HTTP API for production
- Custom Django email backend to bypass SMTP port restrictions

---

## Project Architecture

### Custom User Model

One of the most important design decisions was implementing a custom User model extending Django's AbstractBaseUser. This provides:

**Why Custom User Model?**
- Email-based authentication instead of username
- Additional fields: user_type (individual/ngo), status (pending/verified/rejected)
- Flexible for future enhancements
- Complete control over authentication logic

**Implementation:**

