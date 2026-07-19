---
name: Arun Crackers Design System
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#5b4041'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#8f6f71'
  outline-variant: '#e3bdbf'
  surface-tint: '#bc0b3b'
  primary: '#b90538'
  on-primary: '#ffffff'
  primary-container: '#dc2c4f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb2b7'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#4d5d73'
  on-tertiary: '#ffffff'
  tertiary-container: '#66768d'
  on-tertiary-container: '#fdfcff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdadb'
  primary-fixed-dim: '#ffb2b7'
  on-primary-fixed: '#40000d'
  on-primary-fixed-variant: '#92002a'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#d3e4fe'
  tertiary-fixed-dim: '#b7c8e1'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485d'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-lg:
    fontFamily: Work Sans
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Work Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Work Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Work Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Work Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  data-display:
    fontFamily: JetBrains Mono
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  data-label:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Work Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 12px
  container-margin: 20px
---

## Brand & Style

The design system for Arun Crackers is built on a foundation of high-utility professionalism and industrial precision. It targets wholesale and retail environments where speed of transaction and data clarity are paramount. The aesthetic is a hybrid of **Corporate Modern** and **Functional Industrial**, emphasizing high-density information layouts without sacrificing visual breathing room.

The emotional response is one of reliability and "ready-for-work" efficiency. By using a clean, light-filled environment punctuated by high-visibility safety accents, the UI directs the user's attention to critical path actions and numerical accuracy. The style utilizes crisp 1px borders and subtle tonal shifts rather than heavy shadows to maintain a flat, performant interface suitable for long-shift usage.

## Colors

The palette is designed for maximum legibility in high-glare retail environments. 
- **Primary (#f43f5e):** An energetic Rose/Safety Orange used exclusively for "Commit" actions, primary buttons, and critical status indicators.
- **Surface (#f8fafc):** A cool, clean Slate-White used for the main application background to reduce eye strain.
- **Typography (#0f172a):** Deep Slate is used for all primary text to ensure high contrast ratios.
- **Secondary/Supporting (#64748b):** Mid-tone slates are used for secondary information and iconography.
- **Border (#e2e8f0):** A consistent, light gray used for all structural containment.

## Typography

This design system employs a dual-font strategy to balance professional readability with technical accuracy:
- **Work Sans** is used for all interface labels, headings, and instructional text. Its grounded, neutral character ensures the UI feels approachable yet professional.
- **JetBrains Mono** is mandatory for all numerical data, currency values, stock counts, and SKU codes. The fixed-width nature of this font ensures that columns of numbers align perfectly, allowing for instant scanning of totals and quantities.

Use `data-display` for checkout totals and `data-label` for table headers containing numerical metrics.

## Layout & Spacing

The layout follows a **High-Density Fluid Grid** model. Because POS systems require minimal scrolling and maximum "at-a-glance" information, the design system utilizes a compact 4px base unit.

- **Desktop/Terminal:** A 12-column system with tight 12px gutters. Sidebars for "Current Order" summaries should be fixed-width (320px-400px) while the product catalog area remains fluid.
- **Tablet:** An 8-column system with 12px gutters. Primary touch targets must maintain a minimum height of 48px despite the high-density layout.
- **Mobile:** A 4-column system with 16px margins. Numerical keypads should expand to fill the lower half of the viewport.

Spacing between related input groups should be 16px (`md`), while internal padding for cards and data tables should be 12px.

## Elevation & Depth

This system avoids expressive shadows in favor of **Tonal Layering** and **Structural Outlines**.
- **Level 0 (Base):** Background color #f8fafc.
- **Level 1 (Cards/Surface):** Pure White (#ffffff) backgrounds with 1px solid #e2e8f0 borders. This is the primary surface for all interactive content.
- **Level 2 (Modals/Popovers):** Pure White with a very subtle, sharp shadow (0px 4px 6px -1px rgba(15, 23, 42, 0.1)) and a 1px #cbd5e1 border.
- **Active State:** Elements being dragged or interacted with use a 2px stroke of the Primary color rather than a shadow to indicate focus.

## Shapes

The shape language is "Soft" yet disciplined. A **4px default radius (Soft)** is applied to all buttons, input fields, and small UI components. This provides a subtle modern touch without sacrificing the professional, utilitarian feel required for a retail tool. Larger containers like product cards or checkout modals may scale up to **8px (rounded-lg)** to soften the visual impact of large layout blocks.

## Components

- **Buttons:** 
  - *Primary:* Rose background, white text, 4px radius. Use for "Pay", "Add to Cart", "Confirm".
  - *Secondary:* White background, 1px Slate-200 border, Deep Slate text. Use for "Print Receipt", "Edit Item".
- **Numerical Inputs:** Must use JetBrains Mono. Use large "+" and "-" stepper buttons (minimum 44x44px touch target) flanking the input field.
- **Data Tables:** High-density. Row height 40px. 1px horizontal borders only. Use alternating row stripes (Slate-50) for large inventories.
- **Chips/Badges:** For stock status (e.g., "In Stock", "Low Stock"). Use a 2px radius and semi-transparent backgrounds with high-contrast text.
- **Input Fields:** 1px #e2e8f0 border. On focus, the border transitions to #0f172a (Deep Slate) with a 1px inset ring.
- **Action Bar:** A sticky bottom-bar for mobile/tablet containing the total price in `data-display` typography and a full-width Primary button.