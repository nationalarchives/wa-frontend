# Phase 1 Complete: Setup & Assets

## ✅ Completed Tasks

### 1. SCSS Migration

- **Copied all SCSS structure** from wa-wagtail to wa-frontend:
  - `src/styles/config/` - Variables, mixins, functions
  - `src/styles/base/` - Base styles, typography, fonts
  - `src/styles/components/` - ~30 component stylesheets
  - `src/styles/global/` - Header and footer styles
- **Fixed import paths** to use correct relative paths (`../config`)
- **Updated main.scss** to import all components (excluding Tailwind)
- **Compiled successfully**: main.css is 156KB (minified)

### 2. JavaScript Migration

- **Copied custom components** from wa-wagtail:
  - `src/scripts/components/header.js`
  - `src/scripts/components/skip-link.js`
  - `src/scripts/components/table-hint.js`
  - `src/scripts/components/youtube-consent-manager.js`

- **Updated main.js** to initialize custom components before TNA Frontend
- **Compiled successfully**: main.min.js is 48.4KB (minified)

### 3. Static Assets

- **Copied Montserrat.woff2** to `app/static/assets/fonts/`
- **Copied images** including CSS backgrounds to `src/images/`
- **Webpack configured** to handle font and image assets

### 4. Build System

- **Updated package.json** with new dependencies:
  - Added: `js-cookie`, `lite-youtube-embed`
  - Added webpack loaders: `copy-webpack-plugin`, `css-loader`, `sass-loader`, `postcss-loader`, etc.
- **Enhanced webpack.config.js** to:
  - Handle both development and production modes
  - Process fonts and CSS background images
  - Copy image assets
  - Generate source maps
  - Minify JS in production

### 5. Verification

- ✅ SCSS compiles without errors (156KB)
- ✅ JavaScript compiles without errors (48.4KB)
- ✅ All dependencies installed successfully
- ✅ Asset pipeline working correctly

## Build Commands

```bash
# Compile everything
npm run compile

# Development mode with watch
npm run dev

# Individual compilation
npm run compile:css   # Compiles SCSS
npm run compile:js    # Compiles JS with webpack
```

## File Structure (Updated)

```
wa-frontend/
├── src/
│   ├── styles/
│   │   ├── config/          # ✅ NEW: SCSS configuration
│   │   ├── base/            # ✅ NEW: Base styles
│   │   ├── components/      # ✅ NEW: ~30 component styles
│   │   ├── global/          # ✅ NEW: Header/footer styles
│   │   ├── config.scss      # ✅ NEW: Config entry point
│   │   ├── main.scss        # ✅ UPDATED: Imports all components
│   │   ├── font-awesome.scss
│   │   └── ie.scss
│   ├── scripts/
│   │   ├── components/      # ✅ NEW: Custom JS components
│   │   │   ├── header.js
│   │   │   ├── skip-link.js
│   │   │   ├── table-hint.js
│   │   │   └── youtube-consent-manager.js
│   │   ├── main.js          # ✅ UPDATED: Initializes components
│   │   └── analytics.js
│   └── images/              # ✅ NEW: Source images
│       ├── cssBackgrounds/
│       └── placeholder.webp
├── app/
│   └── static/
│       ├── main.css         # ✅ 156KB (compiled)
│       ├── main.min.js      # ✅ 48.4KB (compiled)
│       ├── analytics.min.js
│       └── assets/
│           ├── fonts/
│           │   └── Montserrat.woff2  # ✅ NEW
│           └── images/
├── package.json             # ✅ UPDATED: New dependencies
└── webpack.config.js        # ✅ UPDATED: Enhanced configuration
```

## Known Issues

- **Deprecation warnings** in compiled CSS (from TNA Frontend library, not our code)
- These are warnings only and don't affect functionality
- Will be resolved when TNA Frontend updates to newer Sass syntax

## Next Phase: Template Migration

The remaining work involves converting Django templates to Jinja2:

### To Do:

1. **Copy and convert base templates** (base.html, base_page.html)
2. **Copy and convert component templates** (~60 files)
3. **Copy and convert page templates** (home, info pages, errors)
4. **Create context processors** for navigation data
5. **Create Jinja2 macros** for reusable elements

See **MERGE_PLAN.md** for detailed conversion guidelines.

## Template Conversion Guidelines Quick Reference

### Django → Jinja2 Syntax Changes

- `{% load static %}` → Remove (use `url_for('static', filename='...')`)
- `{% static 'path' %}` → `{{ url_for('static', filename='path') }}`
- `{% url 'view' %}` → `{{ url_for('blueprint.view') }}`
- `{% wagtailcore_tags %}` → Remove (Wagtail-specific)
- `{% trans "text" %}` → `{{ _('text') }}` (if using Flask-Babel)

### Custom Django Tags to Replace

- `{% primary_nav %}` → Context processor + macro
- `{% footer_nav %}` → Context processor + macro
- `{% image obj width-400 %}` → Custom macro or `<img>` tag

---

Generated: January 14, 2026
Phase 1 Duration: ~30 minutes
Status: **COMPLETE** ✅
