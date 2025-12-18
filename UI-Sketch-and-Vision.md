## 1. High-Level Concept

This project is a **learning assistant web app** where a user can:

- Sign up / log in
- Chat naturally with an AI assistant
- Gradually move from casual conversation into **learning mode**
- Automatically generate **personalized 4–6 week learning paths**
- View all their past learning paths (roadmaps) with real content links

The UI should feel:

- **Clean & modern** (like a lightweight version of ChatGPT / Notion)
- **Calm and focused** (no heavy colours or clutter)
- **Friendly** and **non-intimidating** for students

The overall layout is a **three-column dashboard**:

- Left: Chat history (conversations)
- Middle: Active chat
- Right: Learning path summary + list of all paths


---

## 2. Pages Overview

### 2.1. Landing Page (`index.html`)

**Purpose:** Introduce the app, explain what it does, and provide entry points to log in / sign up.

**Key elements:**

- Simple top navbar with:
  - App name / logo (e.g. *“Learning Coach”*)
  - Links: **Home**, **Login**, **Register**
- Hero section:
  - Heading: *“Chat first. Learn smarter.”*
  - Subtext: *“Talk to an AI learning coach that designs a real 4–6 week roadmap around your life.”*
  - CTA buttons:
    - **Get Started (Sign Up)**
    - **Demo (Login)** if already registered
- Small feature cards:
  - “Natural chat”
  - “Personalized learning paths”
  - “Real contents: videos, articles, practice tasks”

**Visual style:**

- Light background, a bit of gradient or subtle pattern
- One illustration or simple icon to represent “AI + learning”
- Clean typography, nice spacing


### 2.2. Authentication Pages (`login.html`, `register.html`)

**Purpose:** Allow users to create an account or log into an existing one.

**Login page UI:**

- Centered card with:
  - Heading: *“Welcome back”*
  - Inputs: **Email**, **Password**
  - Button: **Login**
  - Link: “Don’t have an account? Sign up”
- Clear error messages using `flash()` (e.g. “Invalid credentials”)

**Register page UI:**

- Centered card with:
  - Heading: *“Create your account”*
  - Inputs: **Name**, **Email**, **Password**
  - Button: **Sign Up**
  - Link: “Already have an account? Login”
- Short note about password rule: “At least 6 characters”

**Visual style:**

- White or very light card on soft grey background
- Minimal, clean, “form-first” design
- Input focus states and clear labels


### 2.3. Dashboard (`dashboard.html`)

The dashboard is the **main experience**. It has 3 logical areas:

#### Layout

- **Left column:** Chat history (conversations)
- **Center column:** Active chat window
- **Right column:** User info + learning paths panel

#### 2.3.1. Left: Conversations List

**Purpose:** Show all the user’s chat sessions.

**Elements:**

- Small header: “Chats”
- Button: **+ New chat**
- Scrollable list of conversation items:
  - Title (first user message or custom title)
  - Last updated timestamp
  - Active chat highlighted

**Behavior:**

- Clicking an item reloads dashboard with that conversation as active
- “New chat” creates a fresh, empty conversation

**Visual style:**

- Simple card with list-style items
- Active item has darker background


#### 2.3.2. Center: Chat Window

**Purpose:** Natural conversation + trigger for learning plan.

**Elements:**

- Header:
  - Title: “Learning Assistant”
  - Status badge: “Online”
  - Subtext: *“First normal chat, then learning plan when you’re ready.”*
- Chat window:
  - Scrollable area with messages
  - User messages aligned right with blue gradient bubble
  - Bot messages aligned left with dark bubble
  - When no messages:
    - Friendly welcome message explaining you can chat normally first
- Input area:
  - Text input: “Type anything in English…”
  - **Send** button

**Extra interaction:**

- Typing indicator:
  - 3 animated dots in a bot bubble while waiting for response
- On submit:
  - Immediately append user bubble
  - Disable input + button
  - Show typing indicator
  - On response, hide indicator and append bot bubble

**Visual style:**

- Chat background with subtle dark gradient (like a mini IDE / terminal vibe)
- Rounded corners, shadowed card
- Comfortable spacing between messages


#### 2.3.3. Right: User & Learning Paths Panel

**Purpose:** Provide context + quick access to all learning paths.

**Elements:**

- Greeting: “Hello, {user.name}”
- Short description of how the assistant works
- If there is at least one plan:
  - Highlight card:
    - “Latest learning path”
    - Goal
    - Created date
    - “View latest learning path” button → opens that plan
- Below that:
  - If more than one plan:
    - Section: “All your learning paths:”
    - List of links:
      - `{goal} – {date}`
      - Clicking opens `/learning-path/<plan_id>`

**Visual style:**

- Light card with accent colour badges
- Clean list of links


---

## 3. Learning Path Page (`learning_path.html`)

**Route behavior:**

- `/learning-path` → latest plan  
- `/learning-path/<plan_id>` → specific plan  

**Layout:**

- Two columns:

### 3.1. Left: Plan Summary

**Elements:**

- Title: “Your Learning Plan”
- Created timestamp
- Short explanatory text
- Summary details:
  - Goal
  - Level
  - Hours per week
  - Total weeks
- Back button: “Back to chat”

**Purpose:**

- Immediately tells the user **what this plan is** and **how it was shaped**.


### 3.2. Right: Weekly Roadmap

Each week is shown as a card:

- Header:
  - “Week X – Step Y”
  - Badge: “~ {hours} hours”
- Content:
  - “Main focus: {topic}”
  - “Suggested mode: {mode}”
- Contents section:
  - “Suggested contents:”
  - List items:
    - **Type** (Video / Text / Practice)
    - Link Title (clickable if URL exists)
    - Level note in italic, e.g. `(better for beginners)`

**Visual style:**

- Separate cards per week
- Slight hover elevation
- Consistent typography
- Focus on readability and clarity

**Optional future additions:**

- Checkboxes to mark a week as “Done”
- Progress bar at top: “You have completed X of Y steps”


---

## 4. UX Flow Summary

1. **User signs up / logs in**
2. Lands on **Dashboard**:
   - No chats? A new one is auto-created.
3. Starts chatting:
   - Small talk, routine, feelings, etc.
4. Mentions:
   - wants to learn / work on a skill
5. Chatbot:
   - Asks **goal**
   - Asks **level**
   - Asks **background**
   - Asks **time (hours/week + weeks)**
6. Once all information is collected:
   - Bot internally sends JSON
   - Backend generates learning path and stores it
   - Bot message: learning path created
   - Frontend redirects to **that specific learning path page**
7. User can:
   - Return to dashboard
   - View **latest plan**
   - View **all previous plans**

---

## 5. Visual Design Goals

- **Consistency:** Same font sizes, padding, border radius across cards and chat.
- **Clarity:** Every section clearly labeled (Chats, Learning Assistant, Your Learning Plan, All Paths).
- **Focus:** Minimal distractions; the main focus is on the chat and the roadmap.
- **Friendly:** Tone is soft and helpful, not robotic.

---

## 6. Future Enhancements (Vision)

- Add icons for content type (video, article, practice).
- Add filters on dashboard to show plans by skill (e.g. “Web Dev only”).
- Add a progress tracker for each learning path.
- Allow users to rename learning paths.
- Export learning path as PDF for printing.
- Toggle between light/dark theme.

---

This document describes the **UI sketch and product vision** for your project in a way that is suitable for:

- Final year project documentation
- Presentation / viva
- Handover to a designer or teammate