---
name: Ignite POS
colors:
  surface: '#1e0f10'
  surface-dim: '#1e0f10'
  surface-bright: '#473435'
  surface-container-lowest: '#180a0b'
  surface-container-low: '#271718'
  surface-container: '#2b1b1c'
  surface-container-high: '#372626'
  surface-container-highest: '#423031'
  on-surface: '#f9dcdc'
  on-surface-variant: '#e3bdbf'
  inverse-surface: '#f9dcdc'
  inverse-on-surface: '#3e2c2d'
  outline: '#aa888a'
  outline-variant: '#5b4041'
  surface-tint: '#ffb2b7'
  primary: '#ffb2b7'
  on-primary: '#67001b'
  primary-container: '#ff516a'
  on-primary-container: '#5b0017'
  inverse-primary: '#bc0b3b'
  secondary: '#b9c7e0'
  on-secondary: '#233144'
  secondary-container: '#3c4a5e'
  on-secondary-container: '#abb9d2'
  tertiary: '#64dca0'
  on-tertiary: '#003822'
  tertiary-container: '#1fa46d'
  on-tertiary-container: '#00311d'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdadb'
  primary-fixed-dim: '#ffb2b7'
  on-primary-fixed: '#40000d'
  on-primary-fixed-variant: '#92002a'
  secondary-fixed: '#d5e3fd'
  secondary-fixed-dim: '#b9c7e0'
  on-secondary-fixed: '#0d1c2f'
  on-secondary-fixed-variant: '#3a485c'
  tertiary-fixed: '#82f9ba'
  tertiary-fixed-dim: '#64dca0'
  on-tertiary-fixed: '#002112'
  on-tertiary-fixed-variant: '#005233'
  background: '#1e0f10'
  on-background: '#f9dcdc'
  surface-variant: '#423031'
typography:
  display-bold:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  data-lg:
    fontFamily: JetBrains Mono
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.02em
  data-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  data-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 8px
  margin-screen: 12px
  padding-cell: 6px 8px
---

## Brand & Style
The design system is engineered for high-stakes, high-volume retail environments where speed and legibility are paramount. The personality is industrial, technical, and high-performance, reflecting the "Ignite" name with an energetic yet controlled aesthetic. 

The design style is **High-Contrast Dark Mode** with a focus on **Precision Minimalism**. It utilizes a "Utility-First" approach: every pixel serves a functional purpose. There are no decorative flourishes or non-essential icons. Visual hierarchy is established through extreme contrast between the slate-charcoal backgrounds and the energetic rose accents, ensuring that critical action points (like "Charge" or "Void") are instantly identifiable in a fast-paced checkout environment.

## Colors
The palette is optimized for low-light retail environments to reduce eye strain while maintaining maximum legibility. 
- **Surface Layering:** Use Slate Charcoal (#0f172a) for the application base and Deep Steel (#1e293b) for active panels and modals to create subtle depth without shadows.
- **Accents:** Energetic Rose (#f43f5e) is reserved exclusively for primary actions and focus states. 
- **Functional Colors:** Success, Warning, and Danger colors are used at high saturation levels to ensure inventory alerts and payment statuses are unmistakable.
- **Borders:** Use Slate-500 (#334155) for all structural dividers to maintain a crisp, blueprint-like appearance.

## Typography
This design system employs a dual-font strategy to separate narrative UI elements from critical transactional data.
- **Inter:** Used for navigation, labels, and general interface text. It provides high readability at small scales.
- **JetBrains Mono:** Used for all "Hard Data"—prices, stock counts, quantities, and SKU numbers. The monospaced nature ensures that columns of numbers align perfectly for quick scanning of receipts and inventory lists.
- **Scaling:** On desktop, use `data-lg` for the "Grand Total" and `data-md` for line-item pricing. Avoid font sizes below 11px to maintain accessibility on touchscreen POS terminals.

## Layout & Spacing
The layout follows a **High-Density Grid** model designed for mouse and touch-precision.
- **Grid:** A 12-column fluid system is used, but content blocks are typically grouped into persistent sidebars (Transaction Feed) and main panels (Product Grid).
- **Density:** Margins and gutters are kept to a minimum (8px to 12px) to maximize the number of visible items without scrolling. 
- **Touch Targets:** While density is high, interactive elements must maintain a minimum height of 32px to accommodate touch-based interactions common in retail hardware.
- **Alignment:** All data values in tables must be right-aligned to their monospaced grid to ensure decimal points align vertically.

## Elevation & Depth
In this design system, depth is communicated through **Tonal Layering and Borders** rather than shadows. 
- **Flat Depth:** Use the 1px solid border (#334155) to define all container boundaries. 
- **Z-Index Logic:** Lower surfaces use the darkest Slate (#0f172a). As an element gains "height" or importance (like a pop-up or a selected row), it shifts to the Deep Steel (#1e293b) background.
- **Focus:** Because the environment is dark, elevation is further suggested by "lighting up" the border. A focused input or selected card should replace its standard border with a 2px sharp Energetic Rose (#f43f5e) stroke.

## Shapes
The shape language is rigid and structural.
- **Radius:** A universal 6px (Soft) radius is applied to all buttons, input fields, and panels. This softens the "industrial" feel just enough to differentiate UI elements from the screen edges, without adopting the playfulness of pill-shaped buttons.
- **Consistency:** Never use circular or pill-shaped containers for status indicators or buttons; maintain the 6px rectangular standard throughout to maximize internal space for labels.

## Components
- **Buttons:**
  - **Primary:** Background #f43f5e, Text #f8fafc (Bold). Used for "Pay," "Print," and "Submit."
  - **Secondary:** Background #1e293b, Border 1px #334155. Used for general actions.
  - **Danger:** Background transparent, Border 1px #ef4444, Text #ef4444.
- **Input Fields:** Background #0f172a, 1px Border #334155. When active, use 2px #f43f5e outline. Monospace font for numerical inputs.
- **Product Cards:** Deep Steel background, 1px border. Card contains Product Name (Inter, 12px) and Price (Mono, 14px, Bold).
- **Data Tables:** 1px horizontal dividers only. Row height 32px. Use Zebra-striping (alternating #0f172a and #1e293b) for tables exceeding 10 rows.
- **Status Chips:** Rectangular (6px radius) with subtle background tints and high-contrast text. No icons unless indicating a system error.
- **Transaction Feed:** A vertical list of items. Each row must show `Quantity x Name` on the left and `Total Price` on the right in JetBrains Mono.