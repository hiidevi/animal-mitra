# Animal Mitra - Connecting Animal Helpers in Faridabad

#### Video Demo: [YOUTUBE_URL_AFTER_RECORDING]

#### Description:

Animal Mitra is a web platform that connects animal lovers, individual volunteers, and animal welfare NGOs in Faridabad, India to help street animals in need of rescue, food, and medical care. The platform solves a critical coordination problem: when people encounter injured or hungry street animals, they don't know who to contact for help, and volunteers working independently lack visibility.

## Project Overview

The platform features a searchable directory of verified animal helpers, listings of NGOs with 24/7 emergency services, a dual registration system for individuals and organizations, an admin verification workflow, and personalized user dashboards. Users can search helpers by location and animal type (dogs, cats, cows, birds), view contact information (phone, WhatsApp, Instagram), and reach out immediately during emergencies.

## Technical Stack

Animal Mitra is built with Django 5.0 (Python web framework), PostgreSQL for production database, Bootstrap 5 for responsive design, and deployed on Render's free tier. The application uses a custom user authentication system, environment-based configuration, and a custom email backend to handle deployment constraints.

## File Structure and Explanations

**animalmitra/settings.py** is the main Django configuration file containing all project settings including database configuration (SQLite for development, PostgreSQL for production via dj-database-url), email backend selection (Gmail SMTP for development, Resend HTTP API for production), security settings (SECRET_KEY, ALLOWED_HOSTS, CSRF protection), static files configuration with WhiteNoise, and installed apps. I used python-decouple to read sensitive values from environment variables, keeping secrets out of the codebase entirely.

**accounts/models.py** contains the core data models. The custom User model extends AbstractBaseUser to enable email-based authentication instead of Django's default username system. It includes a user_type field to differentiate between individuals and NGOs, and a status field for the verification workflow (pending/verified/rejected). I chose to create separate IndividualProfile and NGOProfile models with OneToOne relationships to User, rather than a single polymorphic model, because each user type has distinctly different required fields. IndividualProfile stores helper data like name, mobile number, location, animals they help, and social media links. NGOProfile stores organization-specific data like registration number, services offered, capacity, and 24/7 availability. This separation makes form validation clearer and the admin interface more intuitive.

**accounts/views.py** handles all authentication logic including registration, login, logout, and password reset. The register_view implements a dual registration system where users select their type (individual or NGO) and see different form fields accordingly. All new registrations are created with status='pending' to require admin verification before appearing in public listings. The dashboard views (individual_dashboard and ngo_dashboard) fetch user-specific data and display statistics like profile views and calls received. I implemented password reset using Django's built-in views but customized the email templates to match Animal Mitra's branding.

**animalmitra/email_backend.py** is a custom Django email backend that I created to solve a critical deployment issue. Render's free tier blocks SMTP ports (25, 465, 587), which broke the Gmail SMTP integration that worked perfectly locally. After researching alternatives, I implemented a custom backend using Resend's HTTP API instead of SMTP. This backend extends Django's BaseEmailBackend, converts EmailMessage objects to Resend API calls using HTTPS (port 443), and handles HTML/text emails, CC, BCC, and reply-to headers. This solution took several days to implement but permanently solved the email problem without requiring code changes in views since it maintains Django's standard send_mail() interface.

**admin_panel/views.py** contains a custom admin verification interface. I chose to build a custom interface rather than using Django's built-in admin because it needed to be simple enough for non-technical admins and focused solely on the verification task. The admin_panel_view displays all pending users in a card format with user details and one-click verify/reject buttons. The verify and reject actions use AJAX for instant feedback without page reloads. Only verified users appear in public helper and NGO listings, ensuring quality and preventing spam.

**listings/views.py** implements the public-facing pages. The helpers_list and ngos_list views query only verified profiles from the database and pass them to templates. I implemented search and filtering using client-side JavaScript rather than server-side because the dataset is small (expected under 100 helpers), providing instant results without additional server requests and reducing hosting costs.

**templates/** directory contains all HTML templates. base.html is the master template with navbar, messages display, and footer, from which all other templates extend. The registration template (accounts/register.html) uses JavaScript to toggle between individual and NGO form fields based on user selection. Dashboard templates (dashboard/individual.html and dashboard/ngo.html) are customized for each user type with different statistics and information displays. All templates use Django's template language for server-side rendering, Jinja2-style syntax for variables and loops, and Bootstrap 5 classes for responsive design.

**static/images/** contains the project's visual assets including the logo, various favicon sizes for different devices and browsers, Open Graph image for social media sharing, and Twitter card image. These static files are served via WhiteNoise in production.

## Key Design Decisions

The most significant architectural decision was implementing a custom User model extending AbstractBaseUser. This was necessary because I needed email authentication (no username), a user_type field to differentiate individuals from NGOs, and a status field for the verification workflow. While this added complexity initially, it provided the flexibility needed for the dual registration system and future enhancements.

I debated whether to use separate profile models (IndividualProfile and NGOProfile) or a single polymorphic profile with nullable fields. I chose separate models because it makes field requirements explicit - the registration form can enforce that individuals provide a mobile number while NGOs provide a registration number. This also simplifies form validation and creates a clearer admin interface.

For the email system, the custom backend solution was born out of necessity when Render's port restrictions broke the standard SMTP approach. While it took significant time to implement, it taught me about Django's email backend architecture and created a more robust, platform-independent solution. The same codebase now works seamlessly in development (using Gmail) and production (using Resend's API) by simply changing an environment variable.

The verification workflow with three status states (pending/verified/rejected) was designed for safety and quality. Auto-approving all registrations would risk spam and fake profiles. Manual verification ensures that only genuine helpers and organizations appear in public listings, building user trust and maintaining platform quality.

## AI Usage Acknowledgment

I used ChatGPT as a learning assistant throughout this project. It helped me understand Django concepts like AbstractBaseUser and signals, suggested the custom email backend approach when debugging the Render deployment issue, and provided code templates that I modified for Animal Mitra's specific needs. However, all design decisions, feature choices, code understanding, and problem-solving were my own. I can explain every part of the codebase and justify every technical choice made. The AI was a tutor, not the developer.

## Future Plans

If I continue this project, I plan to add geolocation-based helper search, real-time chat between users and helpers, a success stories section with rescue photos, volunteer scheduling calendar, mobile applications for iOS and Android, multi-language support (Hindi and regional languages), donation integration for NGOs, and expansion to other Indian cities. The modular Django app structure makes these enhancements straightforward to implement.

This project represents over 100 hours of learning, development, testing, and deployment. It addresses a real problem in my community and has the potential to help thousands of street animals by connecting people who care with those who can help.
