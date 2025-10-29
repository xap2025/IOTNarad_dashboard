# 📊 IOTNarad Dashboard Layout Diagram

## 🎨 Complete Dashboard Structure

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          BROWSER VIEWPORT (100vw × 100vh)                      │
│                                                                                 │
│  ┌───────────┐  ┌──────────────────────────────────────────────────────────┐  │
│  │           │  │                  MAIN CONTENT AREA                      │  │
│  │  SIDEBAR  │  │              (margin-left: 280px)                      │  │
│  │           │  │                                                          │  │
│  │ 280px     │  │  ┌────────────────────────────────────────────────────┐  │  │
│  │           │  │  │            HEADER BAR                             │  │  │
│  │           │  │  │  ┌─────────────────┐    ┌──────────────────────┐ │  │  │
│  │           │  │  │  │ Page Title      │    │ Date + Live Clock    │ │  │  │
│  │           │  │  │  │ Page Subtitle   │    │ (IST Timezone)       │ │  │  │
│  │           │  │  │  └─────────────────┘    └──────────────────────┘ │  │  │
│  │           │  │  └────────────────────────────────────────────────────┘  │  │
│  │           │  │                                                          │  │
│  │           │  │  ┌────────────────────────────────────────────────────┐  │  │
│  │           │  │  │            KPI CARDS ROW                          │  │  │
│  │           │  │  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │  │  │
│  │           │  │  │  │87.5% │ │  6   │ │4,890 │ │94.8% │            │  │  │
│  │           │  │  │  │Overall│ │Lines │ │Units │ │Quality│            │  │  │
│  │           │  │  │  │  OEE  │ │      │ │Produc│ │ Rate  │            │  │  │
│  │           │  │  │  └──────┘ └──────┘ └──────┘ └──────┘            │  │  │
│  │           │  │  └────────────────────────────────────────────────────┘  │  │
│  │           │  │                                                          │  │
│  │           │  │  ┌──────────────────────────┐ ┌──────────────────────┐ │  │
│  │           │  │  │ Manufacturing Excellence │ │  Production Status  │ │  │
│  │           │  │  │      Dashboard           │ │                      │ │  │
│  │           │  │  │ - Welcome paragraph     │ │ - Lines Running      │ │  │
│  │           │  │  │ - Feature bullet points │ │ - OEE Target         │ │  │
│  │           │  │  │ - View OEE Button       │ │ - Quality Rate       │ │  │
│  │           │  │  └──────────────────────────┘ └──────────────────────┘ │  │
│  │           │  │                                                          │  │
│  │           │  │            (Content Area - Scrollable)                   │  │
│  │           │  └──────────────────────────────────────────────────────────┘  │
│  │           │                                                                 │
│  └───────────┘                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

```

---

## 🔹 **SIDEBAR DETAILED STRUCTURE** (280px width, 100vh height)

```
┌─────────────────────────┐
│   SIDEBAR (Fixed)       │  Position: fixed, left: 0, top: 0
│   Height: 100vh          │  Width: 280px
│   Overflow: hidden      │  Background: Dark gradient
├─────────────────────────┤
│                         │
│  ┌───────────────────┐  │
│  │  admin (Admin)    │  │  Username Display
│  └───────────────────┘  │  (H6, white text, centered)
│          ↓              │  Margin-bottom: 1rem
│    (1rem gap)           │
│                         │
│  ┌───────────────────┐  │
│  │   LOGO SECTION    │  │  Border: rounded (12px all corners)
│  │  ┌─────────────┐  │  │  Background: rgba(255,255,255,0.05)
│  │  │   Logo      │  │  │  Padding: 0.75rem
│  │  │  (110px)    │  │  │
│  │  └─────────────┘  │  │
│  │                   │  │
│  │   IOTNarad        │  │  H4: 1.2rem, white, bold
│  │   IoT Dashboard   │  │  P: 0.75rem, light white
│  └───────────────────┘  │  Margin-bottom: 1rem
│          ↓              │
│    (1rem gap)           │
│                         │
│  ─────────────────────  │  HR Line (divider)
│          ↓              │  Margin: 1rem
│    (1rem gap)           │
│                         │
│  ┌───────────────────┐  │
│  │  NAVIGATION MENU  │  │  Nav Container (flexShrink: 1)
│  │                   │  │  Padding: px-3
│  │  🏠 Home          │  │
│  │  📊 Analytics     │  │  Nav Items:
│  │  🏭 OEE Dashboard │  │  - Icon + Text (white)
│  │  🔧 Devices       │  │  - Padding: 0.625rem
│  │  👤 Profile       │  │  - Border-radius: 0.5rem
│  │  ⚙️ Settings     │  │  - Active state highlight
│  │  ❓ Help          │  │
│  │                   │  │
│  └───────────────────┘  │  (Flexible height)
│                         │
│         (auto)           │  Auto spacing
│          ↓              │
│                         │
│  ┌───────────────────┐  │
│  │  ───────────────  │  │  HR Divider
│  │  🚪 Logout       │  │  Logout Button
│  └───────────────────┘  │  (marginTop: auto - sticks to bottom)
│                         │  Padding-bottom: 1rem
└─────────────────────────┘
```

---

## 🔹 **MAIN CONTENT AREA DETAILED STRUCTURE**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN CONTENT AREA                           │
│                    (calc(100% - 280px))                        │
│                    Background: #f8f9fa                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    HEADER BAR                           │ │
│  │  Background: white, Padding: 1.5rem 2rem                │ │
│  │  ┌──────────────────────┐  ┌──────────────────────────┐ │ │
│  │  │  Page Title          │  │  Date + Clock            │ │ │
│  │  │  (H4, #1a1a2e)      │  │  Format:                 │ │ │
│  │  │                     │  │  "Wednesday, 29 Oct 2025"│ │ │
│  │  │  Page Subtitle      │  │  "14:30:45" (IST)        │ │ │
│  │  │  (P, muted)         │  │  🕐 icon + time          │ │ │
│  │  └──────────────────────┘  └──────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  CONTENT AREA                           │ │
│  │                  Padding: 2rem                         │ │
│  │                                                         │ │
│  │  ┌───────────────────────────────────────────────────┐ │ │
│  │  │            KPI CARDS ROW (4 cards)                │ │ │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │ │ │
│  │  │  │ 87.5%  │ │   6    │ │ 4,890  │ │ 94.8%  │    │ │ │
│  │  │  │ Overall│ │Produc- │ │ Units  │ │Quality │    │ │ │
│  │  │  │  OEE   │ │tion    │ │Produce │ │ Rate   │    │ │ │
│  │  │  │        │ │Lines   │ │  d     │ │        │    │ │ │
│  │  │  │ 🟣 Icon│ │🟢 Icon │ │🟡 Icon │ │🟢 Icon │    │ │ │
│  │  │  └────────┘ └────────┘ └────────┘ └────────┘    │ │ │
│  │  └───────────────────────────────────────────────────┘ │ │
│  │                                                         │ │
│  │  ┌──────────────────────────┐ ┌──────────────────────┐ │ │
│  │  │ Manufacturing Excellence │ │  Production Status  │ │ │
│  │  │    Dashboard            │ │                      │ │ │
│  │  │                         │ │  • Lines Running    │ │ │
│  │  │  Welcome paragraph      │ │  • OEE Target       │ │ │
│  │  │  • Feature 1            │ │  • Quality Rate     │ │ │
│  │  │  • Feature 2            │ │                      │ │ │
│  │  │  • Feature 3            │ │                      │ │ │
│  │  │  • Feature 4            │ │                      │ │ │
│  │  │                         │ │                      │ │ │
│  │  │  [View OEE Dashboard]   │ │                      │ │ │
│  │  └──────────────────────────┘ └──────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📐 **DIMENSIONS & SPACING**

### **Sidebar (280px)**
- **Width**: 280px (fixed)
- **Height**: 100vh (full viewport)
- **Position**: Fixed (left: 0, top: 0)
- **Background**: Linear gradient (#1a1a2e → #16213e)
- **Z-index**: 1000

### **Main Content**
- **Width**: calc(100% - 280px)
- **Margin-left**: 280px
- **Background**: #f8f9fa (light grey)
- **Min-height**: 100vh

### **Header Bar**
- **Height**: Auto
- **Padding**: 1.5rem (vertical) × 2rem (horizontal)
- **Background**: White
- **Border-bottom**: 1px solid #e9ecef

### **Content Area**
- **Padding**: 2rem (all sides)
- **Scrollable**: Yes (vertical only)

---

## 🎯 **COMPONENT DETAILS**

### **1. Sidebar Logo Section**
- **Container**: Rounded border (12px)
- **Logo Image**: Max 110px width/height
- **Text**: IOTNarad (H4) + IoT Dashboard (P)
- **Spacing**: 1rem gaps

### **2. Navigation Items**
- **Count**: 7 items (Home, Analytics, OEE, Devices, Profile, Settings, Help)
- **Style**: White text + icons
- **Active State**: Lighter background
- **Padding**: 0.625rem vertical, 1.25rem horizontal

### **3. KPI Cards**
- **Count**: 4 cards
- **Layout**: Horizontal row (Bootstrap Grid)
- **Content**: Icon + Large number + Label
- **Colors**: Purple, Green, Yellow, Green

### **4. Date & Clock**
- **Date Format**: "Wednesday, 29 October 2025"
- **Time Format**: "14:30:45" (24-hour, IST)
- **Update**: Every 1 second (dcc.Interval)
- **Timezone**: Asia/Kolkata (IST)

---

## 🔄 **DYNAMIC ELEMENTS**

### **Callbacks:**
1. **Clock Update** - Updates every 1 second
2. **Date Display** - Updates every 1 second
3. **Username Display** - From session store
4. **Page Content** - Changes based on navigation
5. **Active Nav State** - Highlights current page

### **Data Stores:**
- `session-store` - User authentication & data
- `active-page-store` - Current page state
- `device-data-store` - Device information

---

## 🎨 **COLOR SCHEME**

### **Sidebar:**
- Background: Dark gradient (#1a1a2e → #16213e)
- Text: White (#ffffff)
- Icons: White
- Active Nav: rgba(255,255,255,0.15)
- Border: rgba(255,255,255,0.1)

### **Main Content:**
- Background: #f8f9fa (light grey)
- Header: White
- Cards: White with shadow
- Text: #1a1a2e (dark)
- Muted: #6c757d

---

## 📱 **RESPONSIVE BREAKPOINTS**

### **Desktop (>1200px):**
- Sidebar: 280px
- Main: calc(100% - 280px)

### **Tablet (≤1200px):**
- Sidebar: 250px
- Main: calc(100% - 250px)

---

## 🔧 **TECHNICAL SPECS**

### **Layout Type:**
- Fixed Sidebar + Fluid Main Content
- Flexbox Layout
- No horizontal scroll
- Vertical scroll only in content area

### **Technologies:**
- Dash + Bootstrap Components
- Custom CSS (assets/sidebar.css)
- Font Awesome Icons
- Real-time updates (dcc.Interval)

---

**Last Updated**: 2025-10-29  
**Version**: Current Dashboard Layout

