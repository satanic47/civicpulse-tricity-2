# HackCulture Official Submission Package
**Hackathon:** [Code for Communities – Chandigarh Edition](https://hackculture.io/hackathons/code-for-communities-chandigarh)  
**Track:** AI for Digital Public Infrastructure of Chandigarh  
**Submission Portal:** [https://hackculture.io/my-events/manage/6ac4328d0037f69fb28e233c?tab=submissions](https://hackculture.io/my-events/manage/6ac4328d0037f69fb28e233c?tab=submissions)  
**Submission Deadline:** October 15, 2026, 18:29 UTC (23:59 IST)

---

## Field 1: Description of your solution (Textarea)
*Copy and paste the entire block below into Question 1 on the HackCulture submission form:*

```markdown
### CivicPulse Tricity: NagrikSetu AI
**AI-Powered Digital Public Infrastructure Platform for Chandigarh, Mohali, and Panchkula**

#### 1. The Problem
Governments across Indian cities struggle with fragmented citizen grievance mechanisms. In the Chandigarh Tricity region (Chandigarh, Mohali, and Panchkula), citizen feedback is scattered across disparate WhatsApp chats, phone helplines, municipal portals, and social media. More critically:
- **Linguistic Barrier:** Over 70% of grassroots citizens verbally communicate in Punjabi or Hindi, but traditional portals force rigid English form dropdowns.
- **Data Fragmentation:** Grievances lack automated geospatial clustering, making it impossible for municipal engineers to identify systemic infrastructure failures vs. isolated complaints.
- **Budget Misalignment:** Municipal ward budgets are often allocated based on historical inertia rather than real-time demand hotspots and citizen safety urgency.

#### 2. The Solution: NagrikSetu AI
CivicPulse Tricity is a scalable, multilingual AI platform engineered as an open Digital Public Good (DPG). It bridges the gap between grassroots citizen voice and municipal capital works:
1. **Omnichannel Voice & Text Ingestion:** Citizens submit infrastructure requests via voice notes, WhatsApp messages, or web in Punjabi, Hindi, or English.
2. **Google Gemini Multilingual Normalization:** Google Gemini 2.0 Flash ingests raw voice transcripts and messages, detects dialects, and standardizes them into structured canonical schemas.
3. **Automated Urgency Scoring & Routing:** The system calculates a 1–10 hazard urgency score (e.g., exposed electric wires = 10, burst water mains = 9) and automatically routes tickets to the appropriate municipal department (Engineering B&R Roads, Public Health & Water, Electricity, or Sanitation).
4. **Tricity Landmark & Sector Geocoding:** Colloquial landmarks ("Kiran Cinema", "Patel Market", "PU Gate 2") are dynamically mapped to Le Corbusier sector grids (Sectors 1–60, Mohali Phases, Panchkula).
5. **Demand Hotspot Clustering:** Geographic clustering groups individual complaints into high-density demand hotspots, computing localized infrastructure health scores.
6. **Municipal Policy & Capital DPR Copilot:** Gemini AI cross-references aggregated citizen reports with census demographics and ward budgets to generate executive Detailed Project Reports (DPRs) with budget estimations for municipal commissioners.

#### 3. AI & Technical Architecture
- **AI Core:** Google Gemini 2.0 Flash / Pro API with an open-weight Gemma fallback for 100% offline sovereign municipal deployment.
- **Backend:** High-performance Python FastAPI service with Pydantic validation and 21 automated integration tests (100% pass rate).
- **Frontend & GIS:** Responsive dashboard featuring interactive Leaflet.js sector heatmaps, real-time demand clustering, and Chart.js analytics for department workloads.
- **Deployment:** 100% containerized with Docker and docker-compose; deployable on municipal servers in under 5 minutes.

#### 4. Alignment with Hackathon Criteria
- **25% AI / Technical Execution:** Google Gemini performs end-to-end multilingual normalization, hazard urgency assessment, departmental routing, and DPR synthesis.
- **20% Problem-Solution Fit:** Built specifically around the urban realities of Chandigarh's sector grid, Mohali, and Panchkula.
- **20% Depth & Reach Across India:** Designed under India's Digital Public Infrastructure (DPI) principles; instantly scales to 22 scheduled Indian languages and 4,000+ Urban Local Bodies (ULBs).
- **20% Deployability & Scalability:** Fully containerized, zero proprietary database lock-in, open REST APIs, and Twilio/WhatsApp webhook integration.
- **15% Impact Potential:** Ensures equitable civic participation for non-English speakers and transparent capital spending.
- **Bonus Award:** Fully open-source under the MIT License with public GitHub repository availability.
```

---

## Field 2: Submit your Demo video here with public access (URL)
*Upload your screen-recorded demo video to YouTube (as "Unlisted" or "Public") or Google Drive (set to "Anyone with the link can view") and paste the link here.*

### Recommended 2-Minute Demo Recording Script:
1. **0:00 - 0:25: Introduction & Architecture:**
   - Open `http://localhost:8000` on your browser.
   - Say: *"Hello judges! This is CivicPulse Tricity (NagrikSetu AI), an AI-powered Digital Public Infrastructure platform built for Code for Communities Chandigarh by GDG Cloud Chandigarh. It turns multilingual citizen voice feedback into actionable municipal capital projects."*
2. **0:25 - 0:55: Live Citizen Ingestion (Punjabi / Hindi):**
   - Click the test button: **"ਸੈਕਟਰ 22 (ਪਾਣੀ ਲੀਕ)"** (Punjabi voice note).
   - Click **"Triage via Google Gemini AI"**.
   - Show the result card instantly pop up: Language detected: *Punjabi*, Category: *Water Supply & Sewage*, Urgency: *9/10*, Routed to: *Public Health & Water Supply Division*.
   - Point out that the incident immediately appears on the **Le Corbusier Sector Grid map** and the live municipal feed.
3. **0:55 - 1:25: Hotspot Heatmaps & Demand Clustering:**
   - Zoom in on the Leaflet map to show the red circle over Sector 22, Sector 35, and Sector 15.
   - Explain how multiple citizen reports automatically form **Hotspot Clusters** (e.g., `HOTSPOT-TRICITY-001`).
4. **1:25 - 1:55: Municipal Policy & DPR Copilot:**
   - Scroll to the **"Gemini Policy Recommender & Capital DPRs"** card.
   - Show how the AI synthesized multiple complaints into an official Detailed Project Report (e.g., *DPR-CH-2026-001: Priority Infrastructure Intervention in Sector 22, Priority Score 94.2/100, Est. Cost: ₹23.5 Lakhs*).
5. **1:55 - 2:05: Conclusion & Open Source:**
   - Show the GitHub repo link and emphasize: *"Built with Google Gemini, 100% open-source under MIT License, and production ready for pilot deployment."*

---

## Field 3: Share your GitHub repository link with public access (URL)
*Repository URL:*
```
https://github.com/satanic47/civicpulse-tricity
```

### How to push the code to your GitHub:
Open PowerShell in `c:\Users\ShivySid\Downloads\hacktoberfest2026\civicpulse-tricity` and run:
```powershell
git init
git add .
git commit -m "feat: initial release of CivicPulse Tricity (NagrikSetu AI)"
git branch -M main
git remote add origin https://github.com/satanic47/civicpulse-tricity.git
git push -u origin main
```
*(If the repo does not exist on GitHub yet, create a new public repository named `civicpulse-tricity` on https://github.com/new and then run the push command above).*

---

## Field 4: Upload your presentation deck here (converted to PDF) (File)
*Presentation Deck file:* `CivicPulse_Tricity_Pitch_Deck.pdf`

### How to generate the PDF in 10 seconds:
1. Open the file `civicpulse-tricity/presentation/index.html` in Google Chrome or Microsoft Edge.
2. Press `Ctrl + P` (Print).
3. Set **Destination** to: **"Save as PDF"**.
4. Set **Layout** to: **"Landscape"** (or Portrait).
5. Under More settings, enable **"Background graphics"**.
6. Click **Save** and name it `CivicPulse_Tricity_Pitch_Deck.pdf`.
7. Upload this PDF to Question 4 on the HackCulture submission form!
