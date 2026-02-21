# CloudReady ERP Scorecard - Manufacturing Edition

A comprehensive ERP cloud readiness assessment platform designed specifically for manufacturing companies planning Epicor cloud migration.

## 🎯 What It Does

**Provides clarity on what's broken, what blows up next, and what to fix first.**

The platform delivers:
- Overall Health Score (0-100) weighted across 10 manufacturing pillars
- RAG (Red/Amber/Green) status for each pillar
- Top 10 ranked risks that will derail cloud migration
- Top 10 quick wins (0-30 days, low effort)
- 90-day roadmap with workstreams, owners, and effort levels
- Cloud Gates decision: GO / GO-with-conditions / NO-GO
- Executive 1-pager PDF for stakeholder communication

## 🏗️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Database**: MongoDB
- **UI**: Shadcn/ui + Tailwind CSS
- **Icons**: Lucide React
- **Email**: Ready for Resend integration
- **Payments**: Stripe integration structure (to be activated)
- **PDF**: React-PDF (for Executive 1-pager)

## 📋 Features

### Public Features
1. **Landing Page**
   - Value proposition and pain points
   - What you get (6 outputs + Cloud Gates)
   - 10 manufacturing pillars overview
   - Pricing (Tier A Self-Serve & Tier B Guided Review)
   - FAQ section

2. **Assessment Flow**
   - Lead capture form (name, email, company, role, ERP details)
   - 40-question assessment (MVP, database supports 120+)
   - Progress tracking with save draft functionality
   - 0-4 scoring scale with clear labels
   - Notes field for each question
   - Evidence to check hints

3. **Results Dashboard**
   - Overall health score (0-100)
   - Cloud decision (GO/GO-with-conditions/NO-GO)
   - Gate results table (5 gates with PASS/CONDITIONAL/FAIL)
   - Pillar RAG grid (10 pillars with Red/Amber/Green status)
   - Top 10 risks with fix hints
   - Quick wins list (low effort, high impact)
   - 90-day roadmap view
   - Download Executive 1-pager PDF button
   - Export to CSV option

### Admin Panel (`/admin`)
1. **Question Management**
   - View all questions in database
   - Add new questions
   - Edit existing questions
   - Delete questions
   - Configure: QID, Pillar, Gate, Text, Effort, Fix Hints, Risk Text
   - CSV import/export (structure ready)

2. **Pillar Weights**
   - Configure weight for each pillar (P1-P10)
   - Visual validation (must total 100%)
   - Default: P1-P4: 12%, P5-P7: 10%, P8: 8%, P9-P10: 7%

3. **Settings**
   - Currency selection (INR/AED)
   - Pricing configuration for both tiers
   - Guided Review booking link
   - Future: Stripe configuration

## 📊 Data Model

### Collections

1. **questions**
   - id, qid, pillar (P1-P10), gate (G1-G5 or null)
   - text, whyItMatters, evidenceToCheck
   - effort (L/M/H), fixHint, riskText
   - active, sortOrder

2. **profiles**
   - id, name, email, companyName
   - role, erp, epicorVersion, timeline

3. **assessments**
   - id, profileId, email
   - status (DRAFT/COMPLETED/PAID)
   - createdAt, completedAt

4. **answers**
   - id, assessmentId, questionId
   - score (0-4), notes

5. **results**
   - id, assessmentId
   - overallScore, pillarResults, gateResults
   - topRisks, quickWins, roadmap, decision

6. **settings**
   - id, weights (pillar weights)
   - currency, pricing (tierA/tierB for INR/AED)
   - guidedReviewLink

## 🧮 Scoring Logic

### Pillar Scores
```
PillarScore% = average(question scores) / 4 * 100
PillarWeighted = PillarScore% * PillarWeight
OverallScore = SUM(PillarWeighted) * 100
```

### RAG Status (per pillar)
- Green: >= 75%
- Amber: 50-74%
- Red: < 50%

### Risk Ranking
- Any question score 0 or 1 becomes a risk
- RiskScore = (4 - Score) * PillarWeight
- Sorted descending, top 10 selected

### Quick Wins
- Risk items where Effort = L (Low)
- Sorted by RiskScore descending, top 10 selected

### Cloud Gates
5 Gates assessed:
- G1: Data Readiness
- G2: Process Stability
- G3: Customization Risk
- G4: Controls & Security
- G5: Testing & Change Readiness

**Gate Status:**
- PASS: Average score >= 3.0
- CONDITIONAL: Average score 2.5-2.99
- FAIL: Average score < 2.5

**Decision Logic:**
- If any gate FAIL → NO-GO
- Else if 2+ gates CONDITIONAL → GO with conditions
- Else → GO

## 🚀 Setup & Installation

### Prerequisites
- Node.js 18+ and Yarn
- MongoDB running locally or connection URL

### Environment Variables

Create or update `/app/.env`:

```env
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=erp_scorecard

# App URL
NEXT_PUBLIC_BASE_URL=https://scorecloud.preview.emergentagent.com

# Email (add when ready)
# RESEND_API_KEY=your_resend_api_key

# Stripe (add when ready)
# STRIPE_SECRET_KEY=your_stripe_secret_key
# STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
# STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# NextAuth
NEXTAUTH_SECRET=change_in_production
NEXTAUTH_URL=https://scorecloud.preview.emergentagent.com
```

### Installation

```bash
# Install dependencies
cd /app
yarn install

# Start development server
yarn dev

# Server runs on http://localhost:3000
```

### First Run
The application automatically seeds:
- 40 MVP questions (Q1-Q40)
- Default pillar weights
- Default pricing (INR: ₹14,999 / ₹1,50,000, AED: 550 / 5,500)
- Default settings

## 🔌 Integration Status

### ✅ Ready for Integration

1. **Email Service (Resend)**
   - Service structure created at `/app/lib/email-service.js`
   - Template ready for results summary
   - Add `RESEND_API_KEY` to activate
   - Uncomment integration code in email service

2. **Stripe Payments**
   - UI/flow implemented
   - Payment wall structure ready
   - Add Stripe keys to activate checkout
   - Webhook handler structure ready

3. **PDF Generation**
   - React-PDF ready to implement
   - Executive 1-pager layout specified
   - Print-friendly results view available

### 🎯 MVP Scope Complete

- ✅ Landing page with pricing
- ✅ Lead capture form
- ✅ 40-question assessment
- ✅ Scoring engine (all algorithms)
- ✅ Results dashboard (all 6 outputs + Gates)
- ✅ Admin panel (questions, weights, settings)
- ✅ Database model (supports 120+ questions + Epicor Add-on)
- ✅ Email service structure
- ⏳ PDF export (structure ready)
- ⏳ Stripe integration (UI ready)
- ⏳ NextAuth authentication (to be implemented)

## 📍 Routes

- `/` - Main application (landing → lead capture → assessment → results)
- `/admin` - Admin panel (question management, weights, settings)
- `/api/questions` - Get active questions
- `/api/settings` - Get application settings
- `/api/start-assessment` - Create profile and assessment
- `/api/save-answers` - Save assessment answers
- `/api/calculate-results` - Calculate and save results
- `/api/admin/questions` - CRUD operations for questions
- `/api/admin/settings` - Update settings

## 🎨 Design System

### Colors
- Primary: Blue (#2563eb)
- Success/Green: #10b981
- Warning/Amber: #f59e0b
- Error/Red: #ef4444
- Gray scale for backgrounds and text

### Components
All UI components use Shadcn/ui:
- Button, Card, Input, Select, Textarea
- Table, Badge, Progress
- Tabs, Dialog, Toast
- Form components with validation

## 📈 Future Enhancements

### Immediate Next Steps (Post-MVP)
1. Add Resend API key and activate email sending
2. Implement Stripe payment flow
3. Add PDF generation with React-PDF
4. Implement NextAuth for user authentication
5. Add CSV export functionality

### Phase 2 Features
1. Expand to 120 questions (full assessment)
2. Add Epicor Add-on module (20+ questions)
3. Multi-language support
4. Advanced analytics dashboard
5. Historical assessment tracking
6. Comparison reports (before/after)
7. Team collaboration features
8. Custom branding options

## 🧪 Testing

### Manual Testing Checklist

1. **Landing Page**
   - [ ] All sections render correctly
   - [ ] Pricing displays in correct currency
   - [ ] CTA buttons work

2. **Assessment Flow**
   - [ ] Lead capture form validates required fields
   - [ ] Assessment loads 40 questions
   - [ ] Progress bar updates correctly
   - [ ] Save draft functionality works
   - [ ] Can navigate forward/backward
   - [ ] Score selection saves properly

3. **Results**
   - [ ] Overall score calculates correctly
   - [ ] Gate status shows correct PASS/CONDITIONAL/FAIL
   - [ ] Pillar RAG colors are accurate
   - [ ] Top 10 risks sorted by risk score
   - [ ] Quick wins show only low effort items
   - [ ] 90-day roadmap generates

4. **Admin Panel**
   - [ ] Questions load and display
   - [ ] Can add/edit/delete questions
   - [ ] Weights can be modified
   - [ ] Settings save correctly
   - [ ] Currency changes reflect on landing page

### API Testing

```bash
# Get questions
curl http://localhost:3000/api/questions

# Get settings
curl http://localhost:3000/api/settings

# Start assessment
curl -X POST http://localhost:3000/api/start-assessment \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","companyName":"Test Co"}'
```

## 🐛 Known Issues / TODO

1. **Authentication**: NextAuth not yet implemented (admin panel is public)
2. **PDF Export**: React-PDF implementation pending
3. **Email**: Requires Resend API key to send actual emails
4. **Stripe**: Payment integration structure ready but not connected
5. **CSV Export**: Export button present but backend logic needed

## 📝 Deployment Notes

### Production Checklist
1. Update `NEXTAUTH_SECRET` with secure random string
2. Add production MongoDB connection URL
3. Configure Resend API key for email
4. Set up Stripe keys and webhooks
5. Update `NEXT_PUBLIC_BASE_URL` to production domain
6. Enable authentication on `/admin` routes
7. Set up proper error tracking (Sentry, etc.)
8. Configure CORS origins appropriately

### Environment-Specific Settings
- Development: Uses local MongoDB, mock email
- Production: Requires external MongoDB, real email service, payment processor

## 🤝 Support

For questions about implementation or customization, refer to:
- Next.js documentation: https://nextjs.org/docs
- MongoDB documentation: https://docs.mongodb.com
- Shadcn/ui components: https://ui.shadcn.com

## 📄 License

Proprietary - CloudReady ERP Solutions

---

**Built for Manufacturing Excellence** 🏭
