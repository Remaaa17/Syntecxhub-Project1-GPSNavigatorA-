# 🎨 UI Quick Reference Guide

## **Color Palette**

### **Primary Colors:**
```
Indigo Primary:     #4F46E5  ████  (Buttons, accents, links)
Indigo Dark:        #4338CA  ████  (Hover states)
```

### **Neutral Colors:**
```
Background:         #F8FAFC  ████  (Page background)
Card Background:    #FFFFFF  ████  (Cards, panels)
Border:             #E2E8F0  ████  (Borders, dividers)
Light Gray:         #F1F5F9  ████  (KPI backgrounds)
Text Primary:       #334155  ████  (Main text)
Text Secondary:     #475569  ████  (Labels)
Text Dark:          #0F172A  ████  (Headings)
```

### **Semantic Colors:**
```
Success:            #10B981  ████  (Confirmations)
Warning:            #F59E0B  ████  (Alerts)
```

---

## **Typography**

### **Font Family:**
```
Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```

### **Font Sizes:**
```
App Title:          1.25rem (20px) - Bold 700
Card Headers:       0.875rem (14px) - Semibold 600, Uppercase
KPI Labels:         0.75rem (12px) - Regular, Uppercase
KPI Values:         1.75rem (28px) - Bold 700
Body Text:          0.875rem (14px) - Regular
Small Text:         0.75rem (12px) - Regular
```

---

## **Components**

### **Modern Card:**
```css
background: #FFFFFF
border: 1px solid #E2E8F0
border-radius: 0.75rem (12px)
box-shadow: 0 1px 3px rgba(0,0,0,0.1)
```

### **Primary Button:**
```css
background: #4F46E5
color: white
padding: 0.75rem 1.5rem
border-radius: 0.5rem (8px)
font-weight: 600

Hover:
background: #4338CA
transform: translateY(-1px)
box-shadow: 0 4px 6px rgba(79,70,229,0.3)
```

### **Outline Button:**
```css
background: white
color: #334155
border: 1px solid #CBD5E1
padding: 0.75rem 1.5rem
border-radius: 0.5rem
font-weight: 500

Hover:
background: #F8FAFC
border-color: #94A3B8
```

### **Status Badge:**
```css
/* Success */
background: #DCFCE7
color: #166534
border: 1px solid #BBF7D0
padding: 0.5rem 1rem
border-radius: 0.5rem

/* Info */
background: #DBEAFE
color: #1E40AF
border: 1px solid #BFDBFE
```

### **KPI Card:**
```css
background: #F8FAFC
border: 1px solid #E2E8F0
border-radius: 0.5rem
padding: 1rem
text-align: center

Layout:
- Icon (top, 1.25rem, Indigo)
- Label (0.75rem, uppercase, gray)
- Value (1.75rem, bold, dark)
```

### **Direction Step:**
```css
display: flex
padding: 0.75rem
border-bottom: 1px solid #F1F5F9

Icon Circle:
- 32x32px
- background: #F1F5F9
- Indigo icon inside

Content:
- Instruction: 0.875rem, gray-700
- Distance: 0.75rem, gray-500
```

---

## **Layout Measurements**

### **Sidebar:**
```
Width: 340px (desktop)
Position: sticky
Top: 80px
```

### **Map:**
```
Height: 65vh (desktop)
Min-height: 500px
Border-radius: 0.75rem
```

### **Spacing:**
```
Card margin-bottom: 1rem (16px)
Card padding: 1.25rem (20px)
Gap between elements: 0.75rem (12px)
```

---

## **Responsive Breakpoints**

### **Desktop (> 991px):**
- Sidebar: 340px fixed width
- Map: 65vh height
- 2-column layout for stats/directions

### **Mobile (≤ 991px):**
- Sidebar: Full width, stacked
- Map: 400px height
- Single column layout

---

## **Icons Used**

```
Map:                fa-route
Navigation:         fa-directions, fa-arrow-right
Data:               fa-project-diagram, fa-road
Time:               fa-clock
Brain/AI:           fa-brain
Status:             fa-check-circle, fa-info-circle, fa-exclamation-circle
Actions:            fa-download, fa-search-location, fa-eraser
Markers:            fa-map-marker-alt, fa-mouse-pointer
Empty:              fa-route (large, faded)
```

---

## **Animation Timings**

```
Transitions:        0.2s ease-out
Toast Duration:     3 seconds
Fade-in:            0.3s ease-out
Hover Effects:      Immediate (0.2s)
```

---

## **Z-Index Hierarchy**

```
Top Header:         1030 (sticky)
Toast:              9999 (always on top)
Map Overlay:        1000 (Leaflet controls)
Sidebar:            Auto
```

---

## **Common Patterns**

### **Empty State:**
```html
<div class="empty-state">
    <i class="fas fa-route"></i>
    <p class="mb-0">Message here</p>
</div>
```

### **Status Badge:**
```html
<div class="status-badge status-badge-success w-100 justify-content-center">
    <i class="fas fa-check-circle"></i>
    <span>Success Message</span>
</div>
```

### **KPI Grid:**
```html
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-icon"><i class="fas fa-icon"></i></div>
        <div class="kpi-label">Label</div>
        <div class="kpi-value">123</div>
    </div>
</div>
```

### **Direction Step:**
```html
<div class="direction-step">
    <div class="step-icon">
        <i class="fas fa-arrow-right"></i>
    </div>
    <div class="step-content">
        <div class="step-instruction">Instruction</div>
        <div class="step-distance">0.25 km</div>
    </div>
</div>
```

---

## **CSS Classes Quick Reference**

### **Layout:**
```
.sidebar               - Fixed width sidebar
.main-content          - Flexible main area
.map-container         - Map wrapper with styling
```

### **Cards:**
```
.modern-card           - Base card style
.card-header-clean     - Clean header with border
.card-body-clean       - Consistent body padding
```

### **Stats:**
```
.kpi-container         - 2-column grid
.kpi-card              - Individual KPI card
.kpi-label             - Label text
.kpi-value             - Large number
.kpi-icon              - Icon at top
```

### **Status:**
```
.status-badge          - Base badge style
.status-badge-success  - Green success badge
.status-badge-info     - Blue info badge
```

### **Buttons:**
```
.btn-primary-modern    - Indigo primary button
.btn-outline-modern    - White outline button
```

### **Forms:**
```
.form-label-modern     - Modern label style
.form-select-modern    - Modern select dropdown
.form-control-modern   - Modern text input
```

### **Directions:**
```
.directions-list       - Scrollable container
.direction-step        - Individual step
.step-icon             - Circular icon
.step-content          - Text content
.step-instruction      - Instruction text
.step-distance         - Distance text
```

### **Utility:**
```
.empty-state           - Centered empty message
.info-pill             - Small rounded badge
.fade-in               - Fade-in animation
```

---

## **Design Tokens**

```javascript
// Borders
border-width: 1px
border-color: #E2E8F0
border-radius: 0.5rem (small), 0.75rem (medium), 9999px (pill)

// Shadows
box-shadow: 0 1px 3px rgba(0,0,0,0.1)  // sm
box-shadow: 0 4px 6px rgba(0,0,0,0.1)  // md

// Spacing
padding: 1rem, 1.25rem (cards)
margin-bottom: 1rem (cards)
gap: 0.75rem (grids)

// Typography
line-height: 1.5 (normal)
letter-spacing: 0.05em (uppercase text)
```

---

## **Accessibility Notes**

✅ **Contrast Ratios:**
- Text on white: 4.5:1 minimum
- Button text: 4.5:1 minimum
- Icons: Meet WCAG AA standards

✅ **Focus States:**
- Indigo ring: 3px with transparency
- Visible on keyboard navigation

✅ **ARIA:**
- Preserved from Bootstrap
- Proper labels on interactive elements

---

**🎨 Use this reference when customizing or extending the UI!**
