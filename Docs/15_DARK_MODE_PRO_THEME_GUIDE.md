# Dark Mode Pro Theme Specifications
**Preserved from Original OlDocs SD-DarkMaster-Pro Design**  
**Last Updated:** 2025-01-24 22:40 UTC  
**Version:** 1.0.0

---

## 🎨 **Dark Mode Pro Aesthetic Specification**

### **Color Palette**
- **Primary:** Deep black (#111827) - Main backgrounds and containers
- **Accent:** Electric green (#10B981) - Highlights, buttons, progress indicators
- **Text:** Cool gray (#6B7280) - Primary text and secondary elements
- **Surface:** Dark surface (#1F2937) - Elevated surfaces and cards
- **Border:** Subtle border (#374151) - Borders and dividers
- **Gradient:** Linear gradient from deep black to dark green with cool gray accents

### **Typography System**
- **Headers:** 'Roboto' Bold - Professional, clean sans-serif for titles
- **Code:** 'Fira Code' - Monospace with ligatures for technical content
- **Body:** 'Roboto' Regular - Consistent sans-serif for readability

### **Visual Theme Implementation**
```css
:root {
  /* Primary Color Palette */
  --darkpro-primary: #111827;      /* Deep black backgrounds */
  --darkpro-accent: #10B981;       /* Electric green highlights */
  --darkpro-text: #6B7280;         /* Cool gray text */
  --darkpro-surface: #1F2937;      /* Elevated surfaces */
  --darkpro-border: #374151;       /* Subtle borders */
  
  /* Gradients */
  --darkpro-gradient-primary: linear-gradient(135deg, #111827 0%, #1F2937 50%, #10B981 100%);
  --darkpro-gradient-accent: linear-gradient(90deg, #10B981 0%, #059669 100%);
  
  /* Typography */
  --darkpro-font-header: 'Roboto', sans-serif;
  --darkpro-font-code: 'Fira Code', monospace;
  --darkpro-font-body: 'Roboto', sans-serif;
  
  /* Spacing and Layout */
  --darkpro-spacing-xs: 0.25rem;
  --darkpro-spacing-sm: 0.5rem;
  --darkpro-spacing-md: 1rem;
  --darkpro-spacing-lg: 1.5rem;
  --darkpro-spacing-xl: 2rem;
  
  /* Animation and Transitions */
  --darkpro-transition-fast: 0.15s ease-in-out;
  --darkpro-transition-normal: 0.3s ease-in-out;
  --darkpro-transition-slow: 0.5s ease-in-out;
}
```

---

## 🖥️ **Streamlit Theme Configuration**

### **Primary Theme File (streamlit/config.toml)**
```toml
[theme]
primaryColor = "#10B981"
backgroundColor = "#111827"
secondaryBackgroundColor = "#1F2937"
textColor = "#6B7280"
font = "sans serif"
```

### **Advanced Streamlit Styling**
```python
# Custom CSS for Streamlit Dark Mode Pro
st.markdown("""
<style>
/* Dark Mode Pro Base Styling */
.stApp {
    background: linear-gradient(135deg, #111827 0%, #1F2937 50%, #10B981 100%);
    color: #6B7280;
}

/* Header Styling */
.stTitle h1 {
    color: #10B981;
    font-family: 'Roboto', sans-serif;
    font-weight: bold;
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
    color: white;
    border: none;
    border-radius: 0.5rem;
    transition: all 0.3s ease-in-out;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* Sidebar Styling */
.css-1d391kg {
    background: #1F2937;
    border-right: 1px solid #374151;
}

/* Card Styling */
.stContainer {
    background: #1F2937;
    border: 1px solid #374151;
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin: 1rem 0;
}

/* Progress Bar Styling */
.stProgress > div > div {
    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
}
</style>
""", unsafe_allow_html=True)
```

---

## 🎭 **Gradio Custom Styling**

### **Gradio Theme Override (gradio_theme.css)**
```css
/* Gradio Dark Mode Pro Override */
.gradio-container {
  background: var(--darkpro-primary) !important;
  color: var(--darkpro-text) !important;
  font-family: var(--darkpro-font-body) !important;
}

/* Button Styling */
.gr-button-primary {
  background: var(--darkpro-gradient-accent) !important;
  border: none !important;
  color: white !important;
  border-radius: 0.5rem !important;
  transition: var(--darkpro-transition-normal) !important;
}

.gr-button-primary:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3) !important;
}

/* Input Styling */
.gr-input, .gr-dropdown {
  background: var(--darkpro-surface) !important;
  border: 1px solid var(--darkpro-border) !important;
  color: var(--darkpro-text) !important;
  border-radius: 0.5rem !important;
}

/* Tab Styling */
.gr-tab-nav {
  background: var(--darkpro-surface) !important;
  border-bottom: 1px solid var(--darkpro-border) !important;
}

.gr-tab-nav button {
  background: transparent !important;
  color: var(--darkpro-text) !important;
  border: none !important;
  transition: var(--darkpro-transition-fast) !important;
}

.gr-tab-nav button.selected {
  background: var(--darkpro-accent) !important;
  color: white !important;
}

/* Progress Bar */
.gr-progress {
  background: var(--darkpro-surface) !important;
  border-radius: 0.5rem !important;
}

.gr-progress-bar {
  background: var(--darkpro-gradient-accent) !important;
  border-radius: 0.5rem !important;
}
```

---

## 📱 **Mobile Dark Mode Optimization**

### **Mobile-Specific Styling**
```css
/* Mobile Dark Mode Pro Optimization */
@media (max-width: 768px) {
  .stApp {
    background: #111827; /* Solid dark background for OLED efficiency */
  }
  
  /* Touch-friendly buttons */
  .stButton > button {
    min-height: 44px; /* iOS guideline minimum */
    font-size: 16px;
    padding: 0.75rem 1.5rem;
  }
  
  /* Mobile navigation */
  .stSidebar {
    background: #1F2937;
    border-right: none;
  }
  
  /* Card touch optimization */
  .stContainer {
    margin: 0.5rem;
    padding: 1rem;
    border-radius: 1rem;
  }
  
  /* Text sizing for readability */
  .stMarkdown {
    font-size: 16px;
    line-height: 1.6;
  }
}
```

---

## 🚀 **Theme Engine Implementation**

### **DarkPro Theme Engine Class**
```python
class DarkProThemeEngine:
    """
    Dark Mode Pro theme engine for SD-DarkMaster-Pro Unified
    Handles cross-framework theme consistency
    """
    
    def __init__(self):
        self.colors = {
            'primary': '#111827',
            'accent': '#10B981',
            'text': '#6B7280',
            'surface': '#1F2937',
            'border': '#374151'
        }
        
        self.fonts = {
            'header': 'Roboto, sans-serif',
            'code': 'Fira Code, monospace',
            'body': 'Roboto, sans-serif'
        }
    
    def apply_streamlit_theme(self):
        """Apply Dark Mode Pro theme to Streamlit"""
        return f"""
        <style>
        :root {{
            --darkpro-primary: {self.colors['primary']};
            --darkpro-accent: {self.colors['accent']};
            --darkpro-text: {self.colors['text']};
            --darkpro-surface: {self.colors['surface']};
            --darkpro-border: {self.colors['border']};
        }}
        
        .stApp {{
            background: linear-gradient(135deg, {self.colors['primary']} 0%, {self.colors['surface']} 50%, {self.colors['accent']} 100%);
            color: {self.colors['text']};
        }}
        </style>
        """
    
    def apply_gradio_theme(self):
        """Apply Dark Mode Pro theme to Gradio"""
        return f"""
        .gradio-container {{
            background: {self.colors['primary']} !important;
            color: {self.colors['text']} !important;
            font-family: {self.fonts['body']} !important;
        }}
        
        .gr-button-primary {{
            background: linear-gradient(90deg, {self.colors['accent']} 0%, #059669 100%) !important;
            border: none !important;
            color: white !important;
        }}
        """
    
    def get_config_toml(self):
        """Generate Streamlit config.toml theme section"""
        return f"""
        [theme]
        primaryColor = "{self.colors['accent']}"
        backgroundColor = "{self.colors['primary']}"
        secondaryBackgroundColor = "{self.colors['surface']}"
        textColor = "{self.colors['text']}"
        font = "sans serif"
        """
```

---

## 🎯 **Progressive Disclosure with Dark Theme**

### **Collapsible Sections**
```css
/* Progressive Disclosure Dark Styling */
.darkpro-disclosure-header {
  background: var(--darkpro-surface);
  border: 1px solid var(--darkpro-border);
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: var(--darkpro-transition-normal);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.darkpro-disclosure-header:hover {
  background: var(--darkpro-accent);
  color: white;
  transform: translateY(-1px);
}

.darkpro-disclosure-content {
  background: var(--darkpro-primary);
  border: 1px solid var(--darkpro-border);
  border-top: none;
  border-radius: 0 0 0.5rem 0.5rem;
  padding: 1.5rem;
  animation: slideDown var(--darkpro-transition-normal);
}

.darkpro-disclosure-icon {
  color: var(--darkpro-accent);
  transition: var(--darkpro-transition-fast);
}

.darkpro-disclosure-header.expanded .darkpro-disclosure-icon {
  transform: rotate(180deg);
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}
```

---

## 🎨 **Advanced Visual Elements**

### **Loading Animations**
```css
/* Dark Mode Pro Loading Spinner */
.darkpro-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--darkpro-surface);
  border-top: 3px solid var(--darkpro-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Progress Bar with Glow */
.darkpro-progress {
  background: var(--darkpro-surface);
  border-radius: 1rem;
  padding: 0.25rem;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.darkpro-progress-bar {
  background: var(--darkpro-gradient-accent);
  border-radius: 0.75rem;
  height: 1rem;
  transition: width var(--darkpro-transition-normal);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
}

/* Card Hover Effects */
.darkpro-card {
  background: var(--darkpro-surface);
  border: 1px solid var(--darkpro-border);
  border-radius: 1rem;
  padding: 1.5rem;
  transition: var(--darkpro-transition-normal);
  position: relative;
  overflow: hidden;
}

.darkpro-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.1), transparent);
  transition: left var(--darkpro-transition-slow);
}

.darkpro-card:hover::before {
  left: 100%;
}

.darkpro-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2);
}
```

---

## 🔧 **Implementation Guidelines**

### **Framework Integration Priority**
1. **Streamlit Primary** - Main interface uses full Dark Mode Pro theme
2. **Gradio Fallback** - Consistent theme when Streamlit unavailable
3. **Mobile Optimization** - OLED-friendly solid backgrounds
4. **Accessibility** - High contrast mode available

### **Performance Considerations**
- Use CSS variables for easy theme switching
- Optimize gradients for GPU acceleration
- Minimize animation complexity on mobile
- Cache compiled CSS for faster loading

### **Customization Points**
- Accent color easily changeable via CSS variables
- Typography stack modifiable in font variables
- Animation timing adjustable via transition variables
- Layout spacing consistent via spacing variables

---

## 📚 **Integration with Unified Architecture**

This Dark Mode Pro theme integrates with:
- **Streamlit Dashboard** - Primary interface styling
- **CivitAI Browser** - Consistent dark theme for model browsing
- **Storage Manager** - Dark file browser interface
- **Progress Tracking** - Themed progress bars and status indicators
- **Mobile Layout** - Responsive dark theme optimization

**The Dark Mode Pro theme ensures a consistent, professional aesthetic across all components of SD-DarkMaster-Pro Unified while maintaining optimal performance and accessibility.**

---

**Theme Status:** 🟢 **COMPLETE SPECIFICATION**  
**Integration:** Ready for unified_app.py implementation  
**Compatibility:** Streamlit + Gradio + Mobile responsive
