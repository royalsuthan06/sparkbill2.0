tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "surface-container-low": "#f8fafc",
                "on-secondary-fixed-variant": "#475569",
                "inverse-on-surface": "#f8fafc",
                "surface-bright": "#ffffff",
                "secondary": "#475569",
                "primary-fixed": "#ffe4e6",
                "on-background": "#0f172a",
                "surface": "#ffffff",
                "tertiary-fixed": "#dcfce7",
                "on-tertiary-fixed-variant": "#166534",
                "on-tertiary-container": "#14532d",
                "surface-container-lowest": "#ffffff",
                "error-container": "#fee2e2",
                "on-primary-fixed-variant": "#9f1239",
                "tertiary-fixed-dim": "#86efac",
                "on-surface-variant": "#64748b",
                "surface-variant": "#f1f5f9",
                "on-primary-fixed": "#4c0519",
                "secondary-fixed-dim": "#cbd5e1",
                "primary-fixed-dim": "#fda4af",
                "on-secondary": "#ffffff",
                "surface-container-highest": "#e2e8f0",
                "secondary-container": "#e2e8f0",
                "tertiary": "#10b981",
                "on-error": "#ffffff",
                "inverse-surface": "#1e293b",
                "outline": "#cbd5e1",
                "primary-container": "#f43f5e",
                "on-error-container": "#7f1d1d",
                "on-secondary-container": "#1e293b",
                "surface-container-high": "#f1f5f9",
                "on-primary": "#ffffff",
                "surface-tint": "#f43f5e",
                "outline-variant": "#e2e8f0",
                "on-tertiary": "#ffffff",
                "surface-dim": "#f1f5f9",
                "error": "#ef4444",
                "secondary-fixed": "#f1f5f9",
                "on-tertiary-fixed": "#064e3b",
                "inverse-primary": "#fb7185",
                "background": "#f8fafc",
                "surface-container": "#f1f5f9",
                "on-secondary-fixed": "#0f172a",
                "on-primary-container": "#ffffff",
                "primary": "#f43f5e",
                "on-surface": "#0f172a",
                "tertiary-container": "#dcfce7"
            },
            borderRadius: {
                DEFAULT: "0.125rem",
                lg: "0.25rem",
                xl: "0.5rem",
                full: "0.75rem"
            },
            spacing: {
                unit: "4px",
                gutter: "8px",
                "padding-cell": "6px 8px",
                "margin-screen": "12px"
            },
            fontFamily: {
                "headline-sm": ["Inter"],
                "display-bold": ["Inter"],
                "data-md": ["JetBrains Mono"],
                "data-lg": ["JetBrains Mono"],
                "data-sm": ["JetBrains Mono"],
                "body-md": ["Inter"],
                "body-sm": ["Inter"]
            },
            fontSize: {
                "headline-sm": ["18px", { "lineHeight": "24px", "fontWeight": "600" }],
                "display-bold": ["24px", { "lineHeight": "32px", "fontWeight": "700" }],
                "data-md": ["14px", { "lineHeight": "20px", "fontWeight": "500" }],
                "data-lg": ["20px", { "lineHeight": "28px", "letterSpacing": "-0.02em", "fontWeight": "600" }],
                "data-sm": ["11px", { "lineHeight": "14px", "fontWeight": "500" }],
                "body-md": ["14px", { "lineHeight": "20px", "fontWeight": "400" }],
                "body-sm": ["12px", { "lineHeight": "16px", "fontWeight": "400" }]
            }
        }
    }
}
