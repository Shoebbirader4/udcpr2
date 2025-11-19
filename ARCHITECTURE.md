# UDCPR Master - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                          │
├─────────────────────────────────────────────────────────────────┤
│  React Frontend (Port 3000)    │    Admin UI (Port 3002)        │
│  - Login/Dashboard             │    - Rule Verification         │
│  - Project Wizard              │    - Approve/Reject            │
│  - Evaluation Results          │    - Audit Trail               │
│  - AI Chat (planned)           │                                │
└──────────────┬──────────────────┴────────────────┬──────────────┘
               │                                   │
               │ REST API                          │ REST API
               │                                   │
┌──────────────▼───────────────────────────────────▼──────────────┐
│                    Backend API (Port 3001)                       │
│                      Node.js + Express                           │
├──────────────────────────────────────────────────────────────────┤
│  Routes:                                                         │
│  • /api/auth          - JWT authentication                       │
│  • /api/projects      - CRUD + evaluate                          │
│  • /api/rules         - Query rules                              │
│  • /api/admin         - Verification workflow                    │
└──────┬───────────────────┬───────────────────┬──────────────────┘
       │                   │                   │
       │                   │                   │
┌──────▼──────┐   ┌────────▼────────┐   ┌─────▼──────────────────┐
│  MongoDB    │   │  Rule Engine    │   │  AI Services (Planned) │
│  (Port      │   │  (Python)       │   │  - RAG Service         │
│   27017)    │   │                 │   │  - Vision Pipeline     │
│             │   │  Modules:       │   │  - LLM Workers         │
│ Collections:│   │  • FSI          │   └────────────────────────┘
│ • rules     │   │  • Setbacks     │
│ • projects  │   │  • Parking      │
│ • users     │   │  • Height       │
│ • versions  │   │  • TDR/TOD      │
└─────────────┘   └─────────────────┘
```

## Data Flow

### 1. PDF Ingestion Pipeline

```
┌──────────────┐
│  PDF Files   │
│  - UDCPR     │
│  - DCPR      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 1: PDF → Images (pdf2image)                            │
│  Output: PNG files at 300 DPI                                │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 2: OCR (Tesseract)                                     │
│  Output: Text files + HOCR (with bounding boxes)             │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 3: Table Extraction (Camelot/Tabula)                   │
│  Output: CSV files                                           │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 4: LLM Parsing (OpenAI GPT-4o-mini, temp=0)           │
│  Output: Candidate rule JSON                                 │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 5: Human Verification (Admin UI)                       │
│  Action: Approve/Edit/Reject                                 │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 6: Publish to MongoDB                                  │
│  Output: Versioned rules with checksums                      │
└──────────────────────────────────────────────────────────────┘
```

### 2. Project Evaluation Flow

```
┌─────────────────┐
│  User Creates   │
│  Project via    │
│  Wizard         │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend sends project data to Backend                     │
│  POST /api/projects                                         │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend saves to MongoDB                                   │
│  Status: "draft"                                            │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  User clicks "Run Evaluation"                               │
│  POST /api/projects/:id/evaluate                            │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend calls Rule Engine (Python)                         │
│  Input: Project parameters                                  │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Rule Engine computes:                                      │
│  • FSI (base + bonuses)                                     │
│  • Setbacks (front/side/rear)                               │
│  • Parking (ECS requirements)                               │
│  • Height (max permissible)                                 │
│  • Compliance check                                         │
│  Output: Result + Calculation Traces                        │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend saves result to project                            │
│  Status: "evaluated"                                        │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend displays:                                         │
│  • Compliance status                                        │
│  • FSI analysis                                             │
│  • Setback requirements                                     │
│  • Parking requirements                                     │
│  • Violations (if any)                                      │
│  • Calculation traces with rule citations                   │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### MongoDB Collections

#### 1. rules
```javascript
{
  rule_id: "udcpr_20250130_ch3_s1_r001",
  title: "FSI for Residential Zone",
  jurisdiction: "maharashtra_udcpr",
  version: "udcpr_20250130",
  clause_number: "3.1.2",
  clause_text: "Full clause text...",
  parsed: {
    type: "rule",
    rule_logic: {
      conditions: [
        { field: "use_type", op: "==", value: "Residential" }
      ],
      outputs: [
        { field: "base_fsi", value: 1.0 }
      ]
    }
  },
  source_pdf: {
    filename: "UDCPR_Updated_30Jan2025.pdf",
    page: 45
  },
  created_at: ISODate("2025-01-30T00:00:00Z")
}
```

#### 2. projects
```javascript
{
  _id: ObjectId("..."),
  userId: ObjectId("..."),
  name: "Residential Complex - Andheri",
  jurisdiction: "mumbai_dcpr",
  zone: "Residential",
  plotDetails: {
    area_sqm: 500,
    road_width_m: 12,
    corner_plot: false,
    frontage_m: 20
  },
  buildingDetails: {
    use_type: "Residential",
    proposed_floors: 4,
    proposed_height_m: 12,
    proposed_built_up_sqm: 500
  },
  evaluationResult: {
    rule_version: "udcpr_20250130",
    fsi_result: { ... },
    setback_result: { ... },
    compliant: true,
    violations: [],
    calculation_traces: [ ... ]
  },
  status: "evaluated",
  createdAt: ISODate("..."),
  updatedAt: ISODate("...")
}
```

#### 3. users
```javascript
{
  _id: ObjectId("..."),
  email: "user@example.com",
  password: "$2a$10$...", // bcrypt hash
  name: "John Doe",
  role: "user", // user | admin | municipal_officer
  organization: "ABC Architects",
  verified: true,
  createdAt: ISODate("...")
}
```

#### 4. rule_versions
```javascript
{
  version_id: "udcpr_20250130_143022",
  source_files: ["UDCPR_candidates_1706623822.json"],
  rule_count: 1247,
  created_at: ISODate("..."),
  checksum: "a3f5b8c9d2e1..."
}
```

## Technology Stack

### Frontend
- **Framework**: React 18
- **Routing**: React Router v6
- **State**: Zustand (auth), React Query (server state)
- **Forms**: React Hook Form
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP**: Axios

### Backend
- **Runtime**: Node.js 18
- **Framework**: Express
- **Database**: MongoDB with Mongoose
- **Auth**: JWT (jsonwebtoken)
- **Password**: bcrypt
- **Security**: Helmet, CORS

### Rule Engine
- **Language**: Python 3.10+
- **Validation**: Pydantic
- **Testing**: pytest
- **Database**: pymongo

### Ingestion
- **PDF**: pdf2image, PyPDF2
- **OCR**: Tesseract (pytesseract)
- **Tables**: Camelot, Tabula
- **LLM**: OpenAI API (gpt-4o-mini)

### Infrastructure
- **Containers**: Docker
- **Orchestration**: Docker Compose, Kubernetes
- **Database**: MongoDB 6.0
- **Reverse Proxy**: Nginx (production)

## Security Architecture

### Authentication Flow
```
1. User submits credentials
   ↓
2. Backend validates with bcrypt
   ↓
3. Generate JWT token (7 day expiry)
   ↓
4. Frontend stores in localStorage
   ↓
5. All API requests include: Authorization: Bearer <token>
   ↓
6. Backend middleware validates JWT
   ↓
7. Attach user info to request
```

### Security Measures
- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ CORS configuration
- ✅ Helmet for HTTP headers
- ✅ Input validation
- ✅ RBAC (Role-Based Access Control)
- 🔜 HTTPS enforcement (production)
- 🔜 Rate limiting
- 🔜 Audit logging
- 🔜 Data encryption at rest

## Deployment Architecture (Production)

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                           │
│                    (AWS ALB / Nginx)                         │
└────────┬────────────────────────────────┬───────────────────┘
         │                                │
         ▼                                ▼
┌─────────────────┐              ┌─────────────────┐
│  Frontend Pods  │              │  Backend Pods   │
│  (3 replicas)   │              │  (3 replicas)   │
│  React + Nginx  │              │  Node.js        │
└─────────────────┘              └────────┬────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │  MongoDB Atlas  │
                                 │  (Replica Set)  │
                                 └─────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- Frontend: Stateless, can scale infinitely
- Backend: Stateless API, scale based on load
- MongoDB: Replica set + sharding for large datasets

### Performance Optimization
- API response caching (Redis)
- CDN for static assets
- Database indexing on frequently queried fields
- Connection pooling
- Lazy loading in frontend

### Queue-Based Processing
```
Heavy Jobs → RabbitMQ/Kafka → Workers
- LLM parsing
- Vision extraction
- PDF generation
- Email notifications
```

## Monitoring & Observability

### Metrics to Track
- API response times
- Database query performance
- Rule engine execution time
- LLM API costs
- User activity
- Error rates

### Tools (Recommended)
- Application: Datadog / New Relic
- Logs: ELK Stack / CloudWatch
- Uptime: Pingdom / UptimeRobot
- Errors: Sentry

## Future Enhancements

### Phase 2 (Months 3-6)
- RAG-based AI assistant
- Vision pipeline for drawings
- PDF report generation
- Municipal officer portal

### Phase 3 (Months 6-12)
- Mobile app (React Native)
- Offline mode
- Advanced analytics
- Multi-language support
- White-label solution

## Conclusion

This architecture provides:
- ✅ Separation of concerns
- ✅ Scalability
- ✅ Maintainability
- ✅ Security
- ✅ Testability
- ✅ Production-readiness

The system is designed to handle the complexity of building regulations while maintaining flexibility for future enhancements.
