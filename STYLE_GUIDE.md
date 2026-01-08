# Claude.ai Style Guide (Derived from CSS Assets)

## Overview
- Source: CSS assets referenced in the `https://claude.ai/new` head (iframe content) plus inline ProseMirror styles.
- Architecture: Tailwind CSS build with extensive CSS custom properties (HSL tokens) and `data-theme=claude` / `data-mode` theming.
- Visual tone: warm neutral backgrounds, soft beige surfaces, and a warm orange brand accent; serif typography for assistant responses paired with a clean sans UI.
- Theming: light and dark palettes are defined as HSL tokens and applied via `hsl(var(--token) / <alpha>)`.
- Fonts: Anthropic Sans (UI), Anthropic Serif (responses/heading), JetBrains Mono (code), OpenDyslexic (accessibility), KaTeX fonts (math).

## Color Palette
All core colors are defined as HSL tokens and converted to hex for reference. Use `hsl(var(--token) / <alpha>)` when applying opacity.

### Always
| Token | Light HSL | Light Hex | Dark HSL | Dark Hex |
| --- | --- | --- | --- | --- |
| `always-black` | `0 0% 0%` | `#000000` | `0 0% 0%` | `#000000` |
| `always-white` | `0 0% 100%` | `#ffffff` | `0 0% 100%` | `#ffffff` |

### Accent
| Token | Light HSL | Light Hex | Dark HSL | Dark Hex |
| --- | --- | --- | --- | --- |
| `accent-brand` | `15 63.1% 59.6%` | `#d97757` | `15 63.1% 59.6%` | `#d97757` |
| `accent-main-000` | `15 54.2% 51.2%` | `#c6613f` | `15 54.2% 51.2%` | `#c6613f` |
| `accent-main-100` | `15 54.2% 51.2%` | `#c6613f` | `15 63.1% 59.6%` | `#d97757` |
| `accent-main-200` | `15 63.1% 59.6%` | `#d97757` | `15 63.1% 59.6%` | `#d97757` |
| `accent-main-900` | `0 0% 0%` | `#000000` | `0 0% 0%` | `#000000` |
| `accent-pro-000` | `251 34.2% 33.3%` | `#433872` | `251 84.6% 74.5%` | `#9b87f5` |
| `accent-pro-100` | `251 40% 45.1%` | `#5645a1` | `251 40.2% 54.1%` | `#6c5bb9` |
| `accent-pro-200` | `251 61% 72.2%` | `#9d8de3` | `251 40% 45.1%` | `#5645a1` |
| `accent-pro-900` | `253 33.3% 91.8%` | `#e6e3f1` | `250 25.3% 19.4%` | `#29253e` |
| `accent-secondary-000` | `210 73.7% 40.2%` | `#1b67b2` | `210 65.5% 67.1%` | `#74abe2` |
| `accent-secondary-100` | `210 70.9% 51.6%` | `#2c84db` | `210 70.9% 51.6%` | `#2c84db` |
| `accent-secondary-200` | `210 70.9% 51.6%` | `#2c84db` | `210 70.9% 51.6%` | `#2c84db` |
| `accent-secondary-900` | `211 72% 90%` | `#d3e5f8` | `210 55.9% 24.6%` | `#1c3f62` |

### Background
| Token | Light HSL | Light Hex | Dark HSL | Dark Hex |
| --- | --- | --- | --- | --- |
| `bg-000` | `0 0% 100%` | `#ffffff` | `60 2.1% 18.4%` | `#30302e` |
| `bg-100` | `48 33.3% 97.1%` | `#faf9f5` | `60 2.7% 14.5%` | `#262624` |
| `bg-200` | `53 28.6% 94.5%` | `#f5f4ed` | `30 3.3% 11.8%` | `#1f1e1d` |
| `bg-300` | `48 25% 92.2%` | `#f0eee6` | `60 2.6% 7.6%` | `#141413` |
| `bg-400` | `50 20.7% 88.6%` | `#e8e6dc` | `0 0% 0%` | `#000000` |
| `bg-500` | `50 20.7% 88.6%` | `#e8e6dc` | `0 0% 0%` | `#000000` |

### Border
| Token | Light HSL | Light Hex | Dark HSL | Dark Hex |
| --- | --- | --- | --- | --- |
| `border-100` | `30 3.3% 11.8%` | `#1f1e1d` | `51 16.5% 84.5%` | `#dedcd1` |
| `border-200` | `30 3.3% 11.8%` | `#1f1e1d` | `51 16.5% 84.5%` | `#dedcd1` |
| `border-300` | `30 3.3% 11.8%` | `#1f1e1d` | `51 16.5% 84.5%` | `#dedcd1` |
| `border-400` | `30 3.3% 11.8%` | `#1f1e1d` | `51 16.5% 84.5%` | `#dedcd1` |

### Text
| Token | Light HSL | Light Hex | Dark HSL | Dark Hex |
| --- | --- | --- | --- | --- |
| `text-000` | `60 2.6% 7.6%` | `#141413` | `48 33.3% 97.1%` | `#faf9f5` |
| `text-100` | `60 2.6% 7.6%` | `#141413` | `48 33.3% 97.1%` | `#faf9f5` |
| `text-200` | `60 2.5% 23.3%` | `#3d3d3a` | `50 9% 73.7%` | `#c2c0b6` |
| `text-300` | `60 2.5% 23.3%` | `#3d3d3a` | `50 9% 73.7%` | `#c2c0b6` |
| `text-400` | `51 3.1% 43.7%` | `#73726c` | `48 4.8% 59.2%` | `#9c9a92` |
| `text-500` | `51 3.1% 43.7%` | `#73726c` | `48 4.8% 59.2%` | `#9c9a92` |

### Status
| Token | Light HSL | Light Hex | Dark HSL | Dark Hex |
| --- | --- | --- | --- | --- |
| `danger-000` | `0 58.6% 34.1%` | `#8a2424` | `0 98.4% 75.1%` | `#fe8181` |
| `danger-100` | `0 56.2% 45.4%` | `#b53333` | `0 67% 59.6%` | `#dd5353` |
| `danger-200` | `0 56.2% 45.4%` | `#b53333` | `0 67% 59.6%` | `#dd5353` |
| `danger-900` | `0 50% 95%` | `#f9ecec` | `0 46.5% 27.8%` | `#682626` |
| `success-000` | `125 100% 18%` | `#005c08` | `97 59.1% 46.1%` | `#65bb30` |
| `success-100` | `103 72.3% 26.9%` | `#2f7613` | `97 75% 32.9%` | `#459315` |
| `success-200` | `103 72.3% 26.9%` | `#2f7613` | `97 75% 32.9%` | `#459315` |
| `success-900` | `86 45.1% 90%` | `#e7f1da` | `127 100% 13.9%` | `#004708` |
| `warning-000` | `45 91.8% 19%` | `#5d4704` | `40 71% 50%` | `#da9e25` |
| `warning-100` | `39 88.8% 28%` | `#875a08` | `39 93.4% 35.9%` | `#b17506` |
| `warning-200` | `39 88.8% 28%` | `#875a08` | `39 93.4% 35.9%` | `#b17506` |
| `warning-900` | `38 65.9% 92%` | `#f8eedd` | `45 94.8% 15.1%` | `#4b3902` |

### On-color
| Token | Light HSL | Light Hex | Dark HSL | Dark Hex |
| --- | --- | --- | --- | --- |
| `oncolor-100` | `0 0% 100%` | `#ffffff` | `0 0% 100%` | `#ffffff` |
| `oncolor-200` | `60 6.7% 97.1%` | `#f8f8f7` | `60 6.7% 97.1%` | `#f8f8f7` |
| `oncolor-300` | `60 6.7% 97.1%` | `#f8f8f7` | `60 6.7% 97.1%` | `#f8f8f7` |

### Pictogram
| Token | Light HSL | Light Hex | Dark HSL | Dark Hex |
| --- | --- | --- | --- | --- |
| `pictogram-100` | `50 20.7% 88.6%` | `#e8e6dc` | `48 3.4% 29.2%` | `#4d4c48` |
| `pictogram-200` | `51 16.5% 84.5%` | `#dedcd1` | `60 2.5% 23.3%` | `#3d3d3a` |
| `pictogram-300` | `0 0% 100%` | `#ffffff` | `60 2.1% 18.4%` | `#30302e` |
| `pictogram-400` | `48 33.3% 97.1%` | `#faf9f5` | `60 2.7% 14.5%` | `#262624` |

## Typography
### Font families
- `--font-ui`: Anthropic Sans (300-800, normal + italic). Default UI font (`body, html`).
- `--font-ui-serif` and `--font-claude-response`: Anthropic Serif (300-800, normal + italic). Used for headings and Claude responses.
- `--font-mono`: JetBrains Mono (400) for code, `pre`, `kbd`, `samp`.
- `--font-dyslexia`: OpenDyslexic (400/500) with fallbacks.
- Math: KaTeX families (KaTeX_Main, KaTeX_Math, KaTeX_SansSerif, etc) for math rendering.

### Type scale (UI)
| Class | Font | Size | Line height | Weight | Notes |
| --- | --- | --- | --- | --- | --- |
| `font-display` | Serif | 2.375rem (38px) | 1.2 | 330 | `font-variation-settings: "opsz" 48` |
| `font-title` | Serif | 1.75rem (28px) | 1.3 | 500 | `opsz` 28 |
| `font-heading` | Serif | 1.5rem (24px) | 1.3 | 500 | `opsz` 24 |
| `font-xl-bold` | Sans | 1.25rem (20px) | 1.4 | 600 | `opsz` 20 |
| `font-large-bold` | Sans | 1rem (16px) | 1.4 | 600 | |
| `font-base-bold` | Sans | 0.875rem (14px) | 1.4 | 500 | |
| `font-small-bold` | Sans | 0.75rem (12px) | 1.4 | 600 | |

### Type scale (Claude response)
| Class | Font | Size | Line height | Weight | Notes |
| --- | --- | --- | --- | --- | --- |
| `font-claude-response-title` | Serif | 1.75rem (28px) | 1.3 | 600 | `opsz` 28 |
| `font-claude-response-heading` | Serif | 1.25rem (20px) | 1.4 | 600 | `opsz` 20 |
| `font-claude-response-subheading` | Serif | 1rem (16px) | 1.35 | 600 | |
| `font-claude-response-body-bold` | Serif | 1rem (16px) | 1.5 | 600 | |
| `font-claude-response-small-bold` | Serif | 0.875rem (14px) | 1.5 | 600 | |
| `font-claude-response-code` | Mono | 0.813rem (13px) | 1.5 | 400 | |
| `font-claude-response-code-small` | Mono | 0.688rem (11px) | 1.5 | 400 | |

### Weight conventions
- Light mode base weights: `font-normal` 430, `font-medium` 550, `font-semibold` 580, `font-bold` 600.
- Dark mode adjusts weights slightly: `font-normal` 400, `font-medium` 510, `font-semibold` 540, `font-bold` 530.
- Monospace and code disable ligatures: `font-variant-ligatures: none; font-feature-settings: "calt" 0, "liga" 0`.

## Spacing System
- Primary spacing scale aligns with Tailwind defaults (4px grid): 0.25rem (4px), 0.5rem (8px), 0.75rem (12px), 1rem (16px), 1.5rem (24px), 2rem (32px), 2.5rem (40px), 3rem (48px), 4rem (64px), 6rem (96px), 8rem (128px).
- Micro-spacing values appear for tight UI elements: 0.05rem, 0.2rem, 0.3125rem, 0.5625rem, 0.65rem, 0.6875rem, 0.8125rem.
- Larger layout spacing is often done via arbitrary values: 38px, 40px, 42px, 50px, 96px, 100px, 120px, 160px.
- Responsive padding uses `clamp(...)` and viewport units, e.g. `pl-[clamp(0px,7vw,80px)]`, `pt-[25vh]`.

## Layout & Grid
- Containers use Tailwind `container` widths with breakpoints (640/768/1024/1280/1536px).
- Common max-widths: 48rem, 56rem, 80rem, 90rem, plus many custom `max-w-[1100px]`, `max-w-[1200px]`, `max-w-[1400px]`, `max-w-[75ch]`.
- Layout relies heavily on `flex` and `grid` utilities with breakpoint variants (`md`, `lg`, `xl`).

## Component Styles
### Buttons
- Shape: `rounded-md` (0.375rem) and `rounded-[.625rem]` used in segmented controls.
- Spacing: `px-3` + `py-2` and height utilities like `h-9` (2.25rem).
- States: `data-disabled` applies `opacity-50`, `cursor-not-allowed`, and muted text (`text-text-500`).
- Focus: `focus-visible` rings with `ring-accent-secondary-100` and `ring-offset-2`.

### Inputs / Chat editor (ProseMirror)
- Editor uses `white-space: pre-wrap` and `break-spaces` for multiline input.
- Gap cursor uses a 1px top border and a blinking keyframe (`ProseMirror-cursor-blink`).
- Disabled state removes placeholder and disables editing.

### Panels / Cards
- Typical surface: `bg-bg-100` or `bg-bg-200` with `border border-border-300/15`.
- Hover: subtle background lift to `bg-bg-300` and a hairline border on hover.
- Popovers and menus use `data-popup-open` with a rounded background overlay.

### Accordion / Disclosure
- `AccordionItem` uses `border-b` or `border-b-0.5` with `border-border-300/15`.
- `accordion-open` / `accordion-close` keyframes animate height.

### Toasts
- Named keyframes for toast animations: `ToastComponent_fade__yi0F_` and `ToastComponent_translateX__VOS8B`.

### Code blocks and syntax highlighting
- Highlight.js theme uses One Dark palette: background `#282c34`, base text `#abb2bf`, accents for keywords/strings.
- Code blocks are padded (`1em`) and set to `overflow-x: auto`.

### Scrollbars
- Custom `::-webkit-scrollbar` widths: 0.25rem and 0.375rem.
- Thumb styles: `rounded-full`, `bg-border-400/15` or `bg-text-500/80`, with `bg-clip-padding`.

## Shadows & Elevation
Common shadow tokens (via `--tw-shadow`):
- Subtle elevation: `0 1px 2px 0 rgb(0 0 0/0.05)` (sm).
- Standard: `0 1px 3px 0 rgb(0 0 0/0.1), 0 1px 2px -1px rgb(0 0 0/0.1)`.
- Medium: `0 10px 15px -3px rgb(0 0 0/0.1), 0 4px 6px -4px rgb(0 0 0/0.1)`.
- Large: `0 20px 25px -5px rgb(0 0 0/0.1), 0 8px 10px -6px rgb(0 0 0/0.1)`.
- Custom soft UI shadow: `0 0.25rem 1.25rem hsl(var(--always-black)/3.5%)` with optional hairline border overlay.
- Accent shadow: `0 2px 8px 0 hsl(var(--accent-secondary-200)/16%)`.

## Animations & Transitions
### Keyframes in use
- `accordion-open`, `accordion-close`
- `fade`, `zoom`
- `spin`, `pulse`, `ping`, `blink`
- `shimmer`, `shimmertext`, `loading-background`, `pulse-dot`
- Toast-specific: `ToastComponent_fade__yi0F_`, `ToastComponent_translateX__VOS8B`

### Timing and easing
- Durations: 75ms, 100ms, 150ms, 200ms, 250ms, 300ms, 500ms, 700ms, 1s.
- Easing: `ease-in`, `ease-out`, `ease-in-out` (`cubic-bezier(.4,0,.2,1)`), and custom easings:
  - `cubic-bezier(.19,1,.22,1)` (snappy-out)
  - `cubic-bezier(.165,.85,.45,1)`
  - `cubic-bezier(.17,.67,.3,1.2)`
  - `cubic-bezier(0,.9,.5,1.35)`

## Border Radius
Standard Tailwind radii:
- `rounded-sm` 0.125rem (2px), `rounded` 0.25rem (4px), `rounded-md` 0.375rem (6px), `rounded-lg` 0.5rem (8px)
- `rounded-xl` 0.75rem (12px), `rounded-2xl` 1rem (16px), `rounded-3xl` 1.5rem (24px), `rounded-full` 9999px

Custom radii in use:
- `rounded-[0.4rem]`, `rounded-[0.6rem]`, `rounded-[0.625rem]`, `rounded-[0.65rem]`, `rounded-[0.9rem]`
- `rounded-[12px]`, `rounded-[14px]`, `rounded-[20px]`, `rounded-[24px]`, `rounded-[30px]`, `rounded-[32px]`
- `rounded-[2rem]`, `rounded-[27%]`

## Opacity & Transparency
- Opacity utilities: 0, 0.02, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9, 1.
- Background opacity utilities: `bg-opacity-5`, `bg-opacity-10`, `bg-opacity-20`, `bg-opacity-50`, `bg-opacity-80`.
- Borders often use low alpha: `border-border-300/15`, `border-400/15`, `ring-border-300/50`.
- Example: `bg-bg-000/50`, `text-500/80`, `always-black/8%`.

## Common Tailwind CSS Usage in Project
- Color utilities are tied to CSS variables: `bg-bg-100`, `text-text-300`, `border-border-300/15`.
- Dark mode uses attribute selectors: `dark:` maps to `[data-mode=dark]`, not only `.dark`.
- State variants are heavy: `data-[state=open]`, `data-[highlighted]`, `data-[disabled]`.
- Emphasis on `rounded-*`, `shadow-*`, `backdrop-blur-*`, `ring-*`, and `transition-*` with short durations.
- Layout patterns: `flex`, `grid`, `gap-*`, `space-x-*`, `max-w-*`, `min-h-*`, `line-clamp-*`.

## Example component reference design code
Below is a compact example that mirrors the Claude chat panel style using the same tokens.

```html
<div data-theme="claude" data-mode="light" class="min-h-screen bg-bg-100 text-text-100 font-ui">
  <div class="max-w-3xl mx-auto px-6 py-8">
    <header class="mb-6">
      <h1 class="font-title">New Conversation</h1>
      <p class="font-base text-text-400 mt-2">Warm, neutral surfaces with serif response typography.</p>
    </header>

    <section class="rounded-lg border border-border-300/15 bg-bg-000 shadow-[0_0.25rem_1.25rem_hsl(var(--always-black)/3.5%)] p-4">
      <div class="font-claude-response-title mb-2">Claude</div>
      <div class="font-claude-response-body text-text-200">
        This is a response paragraph set in Anthropic Serif with 1.5 line height.
      </div>
      <pre class="font-claude-response-code bg-bg-000/50 border border-border-400/15 rounded-md mt-4 p-3">
<code>const answer = \"Warm neutral UI\";</code>
      </pre>
    </section>

    <div class="mt-6 rounded-[.625rem] border border-border-300/15 bg-bg-100 p-3">
      <textarea
        class="w-full bg-transparent font-base text-text-100 placeholder:text-text-400 outline-none"
        rows="3"
        placeholder="Message Claude..."
      ></textarea>
      <div class="mt-3 flex justify-end gap-2">
        <button class="rounded-md px-3 py-2 text-text-300 hover:bg-bg-300 transition-colors duration-150">
          Cancel
        </button>
        <button class="rounded-md px-3 py-2 bg-accent-brand text-oncolor-100 shadow-[0_2px_8px_0_hsl(var(--accent-secondary-200)/16%)] transition-colors duration-150">
          Send
        </button>
      </div>
    </div>
  </div>
</div>
```

## Additional Notes
- The UI uses HSL tokens with alpha for fine-grained translucency.
- Dark mode is driven by `data-mode=dark` and also respects `prefers-color-scheme: dark`.
- Some components rely on third-party styles (highlight.js, KaTeX, ProseMirror).
