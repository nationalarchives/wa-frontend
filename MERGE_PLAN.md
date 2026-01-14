# Front-End Merge Plan: wa-wagtail → wa-frontend

## Overview

Merging front-end assets from the Django/Wagtail wa-wagtail project into the Flask wa-frontend project. This involves:

- Copying templates and converting from Django to Jinja2
- Copying SCSS/CSS and JavaScript components
- Excluding Django Pattern Library
- Maintaining consistency with Flask/Jinja2 patterns

## Source Repository Analysis

### wa-wagtail Structure

```
ukgwa/
├── static_src/                    # Source assets
│   ├── sass/
│   │   ├── config/                # Variables, mixins, functions
│   │   ├── base/                  # Base styles, typography, fonts
│   │   ├── components/            # Component-specific SCSS (~30 components)
│   │   ├── global/                # Header, footer
│   │   └── main.scss              # Main entry point
│   ├── javascript/
│   │   ├── components/            # Header, skip-link, table-hint, youtube
│   │   └── main.js                # Main entry point
│   ├── fonts/
│   │   └── Montserrat.woff2
│   └── images/
├── static_compiled/               # Built assets
│   ├── css/main.css
│   ├── js/main.js
│   └── fonts/
└── project_styleguide/
    └── templates/                 # Django templates with Pattern Library
        ├── base.html
        ├── base_page.html
        ├── components/            # ~60 component templates
        ├── pages/                 # Page templates
        └── sprites/

Build System:
- Webpack 5 with TypeScript, Sass
- Uses @nationalarchives/frontend v0.29.1
- Tailwind CSS integration
- PostCSS with autoprefixer
```

### wa-frontend Current Structure

```
app/
├── static/                        # Built assets only
│   ├── main.css
│   ├── main.min.js
│   ├── analytics.min.js
│   ├── font-awesome.css
│   └── assets/
│       ├── fonts/
│       └── images/
└── templates/
    ├── base.html                  # Jinja2 base
    ├── errors/
    └── main/
        ├── index.html
        └── cookies.html

src/
├── styles/
│   ├── main.scss                  # Only imports TNA Frontend
│   ├── font-awesome.scss
│   └── ie.scss
└── scripts/
    ├── main.js                    # Basic TNA Frontend init
    └── analytics.js

Build System:
- Webpack 5 for JS
- Sass CLI for CSS
- Uses @nationalarchives/frontend v0.30.2
- No TypeScript
```

## Merge Strategy

### 1. SCSS/CSS Migration

#### Structure to Create

```
src/styles/
├── config/
│   ├── _variables.scss
│   ├── _mixins.scss
│   └── _functions.scss
├── base/
│   ├── _base.scss
│   ├── _typography.scss
│   └── _fonts.scss
├── components/
│   ├── _accordion.scss
│   ├── _alert-banner.scss
│   ├── _breadcrumb.scss
│   ├── _button.scss
│   ├── _call-to-action.scss
│   ├── _card.scss
│   ├── _card-listing.scss
│   ├── _featured-search.scss
│   ├── _hero.scss
│   ├── _icon.scss
│   ├── _image-block.scss
│   ├── _introduction.scss
│   ├── _listing-item.scss
│   ├── _listing-page.scss
│   ├── _page-header.scss
│   ├── _related-content.scss
│   ├── _responsive-object.scss
│   ├── _rich-text.scss
│   ├── _sf.scss (streamfield)
│   ├── _sidebar.scss
│   ├── _skip-link.scss
│   ├── _stat-block.scss
│   ├── _table.scss
│   ├── _utilities.scss
│   └── _video-embed.scss
├── global/
│   ├── _header.scss
│   └── _footer.scss
├── main.scss (updated)
├── font-awesome.scss (keep)
└── ie.scss (keep)
```

#### Actions

- Copy entire `ukgwa/static_src/sass/` directory structure to `src/styles/`
- Update `main.scss` to import all components
- **EXCLUDE** Tailwind CSS directives (not needed for Flask app)
- Ensure `@use` syntax is maintained (modern Sass)

### 2. JavaScript Migration

#### Structure to Create

```
src/scripts/
├── components/
│   ├── header.js
│   ├── skip-link.js
│   ├── table-hint.js
│   └── youtube-consent-manager.js
├── main.js (updated)
└── analytics.js (keep)
```

#### Actions

- Copy `ukgwa/static_src/javascript/components/` to `src/scripts/components/`
- Update `main.js` to initialize custom components:

  ```javascript
  import {
    initAll,
    Cookies,
  } from "@nationalarchives/frontend/nationalarchives/all.mjs";
  import Header from "./components/header.js";
  import SkipLink from "./components/skip-link.js";
  import YouTubeConsentManager from "./components/youtube-consent-manager.js";
  import TableHint from "./components/table-hint.js";

  function initComponent(ComponentClass) {
    const items = document.querySelectorAll(ComponentClass.selector());
    items.forEach((item) => new ComponentClass(item));
  }

  document.addEventListener("DOMContentLoaded", () => {
    // Cookie domain setup
    const cookiesDomain =
      document.documentElement.getAttribute("data-cookiesdomain");
    if (cookiesDomain) {
      new Cookies({ domain: cookiesDomain });
    }

    // Init custom components
    initComponent(SkipLink);
    initComponent(YouTubeConsentManager);
    initComponent(TableHint);
    initComponent(Header);

    // Init TNA Frontend
    initAll();
  });
  ```

- **Note**: TypeScript files (.ts) will need to be converted to JavaScript (.js) or TypeScript support added to build

### 3. Template Migration (Django → Jinja2)

#### Django to Jinja2 Conversion Rules

| Django Syntax                      | Jinja2 Syntax                                    | Notes                              |
| ---------------------------------- | ------------------------------------------------ | ---------------------------------- | ----------------------- | ------------------- |
| `{% load static %}`                | Remove (use `url_for('static', filename='...')`) | Flask built-in                     |
| `{% load wagtailcore_tags %}`      | Remove                                           | Wagtail-specific                   |
| `{% load navigation_tags %}`       | Remove or convert to macros                      | Custom tags need reimplementation  |
| `{% static 'path' %}`              | `url_for('static', filename='path')`             | Flask URL generation               |
| `{% include "template.html" %}`    | `{% include "template.html" %}`                  | Same syntax ✓                      |
| `{% extends "base.html" %}`        | `{% extends "base.html" %}`                      | Same syntax ✓                      |
| `{% block name %}`                 | `{% block name %}`                               | Same syntax ✓                      |
| `{{ page.title }}`                 | `{{ page.title }}`                               | Same syntax ✓                      |
| `{% if condition %}`               | `{% if condition %}`                             | Same syntax ✓                      |
| `{% for item in items %}`          | `{% for item in items %}`                        | Same syntax ✓                      |
| `{% url 'view_name' %}`            | `{{ url_for('blueprint.view_name') }}`           | Different URL generation           |
| `{% trans "text" %}`               | `{{ _('text') }}`                                | Translation (if using Flask-Babel) |
| `{% wagtailcore_tags %}`           | Remove                                           | Wagtail userbar not needed         |
| `{% image page.image width-400 %}` | Custom macro needed                              | Wagtail-specific image handling    |
| `{{ page                           | social_text }}`                                  | Custom filter needed               | Custom template filters |
| `{% firstof var1 var2 %}`          | `{{ var1 or var2 }}`                             | Different syntax                   |
| `{% spaceless %}`                  | Remove or use Jinja2 whitespace control          | Different approach                 |
| `{{ value                          | title }}`                                        | `{{ value                          | title }}`               | Most filters same ✓ |

#### Templates to Convert

##### Base Templates

```
project_styleguide/templates/
├── base.html → app/templates/layouts/base_page.html
└── base_page.html → app/templates/layouts/base_content.html
```

##### Component Templates

```
components/ → app/templates/components/
├── header/header.html
├── footer/footer.html
├── navigation/
│   ├── primary_nav.html
│   ├── secondary_nav.html
│   ├── sidebar.html
│   ├── breadcrumbs.html
│   ├── footer_nav.html
│   └── footer_links.html
├── alert_banner/
│   ├── alert_banner.html
│   ├── alert_banner--info.html
│   ├── alert_banner--warning.html
│   └── alert_banner--positive.html
├── card/card.html
├── hero/hero.html
├── page_header/page_header.html
├── listing_item/listing_item.html
├── related_content/related_content.html
├── featured_search/featured_search.html
├── cta/call_to_action.html
├── pagination/
│   ├── pagination.html
│   ├── numbered_pagination.html
│   └── index_pagination.html
├── skip_link/skip_link.html
├── responsive_image/responsive_image.html
├── icons/icon.html
├── tabs/
│   ├── tabs.html
│   ├── tabs_nav.html
│   └── tab_nav_item.html
└── streamfield/
    ├── richtext.html
    ├── heading_block.html
    ├── image_block.html
    ├── video_embed_block.html
    ├── quote_block.html
    ├── stat_block.html
    ├── table_block.html
    ├── typed_table_block.html
    ├── accordion_block.html
    ├── call_to_action_block.html
    └── stream_block.html
```

##### Page Templates

```
pages/ → app/templates/pages/
├── home/home_page.html
├── standardpages/
│   ├── index_page.html
│   ├── information_page.html
│   └── login_page.html
├── listing/listing.html
├── errors/
│   ├── 404.html
│   ├── 403.html
│   └── 500.html
└── wagtail/
    └── password_required.html (may not be needed)
```

#### Conversion Steps for Each Template

1. **Remove Django-specific template tags**

   ```django
   {% load static wagtailcore_tags wagtailimages_tags navigation_tags %}
   {% wagtail_site as current_site %}
   ```

   → Remove entirely or convert to Jinja2 imports

2. **Convert static file references**

   ```django
   <link rel="stylesheet" href="{% static 'css/main.css' %}">
   ```

   →

   ```jinja2
   <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
   ```

3. **Convert URL references**

   ```django
   <a href="{% url 'home' %}">
   ```

   →

   ```jinja2
   <a href="{{ url_for('main.index') }}">
   ```

4. **Convert includes**

   ```django
   {% include "components/header/header.html" %}
   ```

   →

   ```jinja2
   {% include "components/header/header.html" %}
   ```

   (Usually no change, but check context passing)

5. **Handle custom template tags**
   - `{% primary_nav %}` → Need to create Jinja2 macro or pass nav data from view
   - `{% footer_nav %}` → Same approach
   - Navigation logic needs to move to Python/context processors

6. **Convert Wagtail-specific tags**
   - `{% wagtailuserbar %}` → Remove (admin feature)
   - `{% image obj width-400 %}` → Create custom macro or use regular `<img>` tags
   - Image handling needs custom implementation

7. **Update context variables**
   - `{{ page.title }}` → Ensure views pass correct context
   - `{{ settings.core.SocialMediaSettings.twitter_handle }}` → Move to config/context processor

8. **Handle conditionals**
   ```django
   {% if GOOGLE_TAG_MANAGER_ID and not request.in_preview_panel %}
   ```
   →
   ```jinja2
   {% if config.GOOGLE_TAG_MANAGER_ID %}
   ```

### 4. Static Assets Migration

#### Fonts

```
Copy: ukgwa/static_src/fonts/Montserrat.woff2
To: app/static/assets/fonts/Montserrat.woff2
```

#### Images

```
Copy: ukgwa/static_src/images/cssBackgrounds/
To: src/images/cssBackgrounds/

Copy: ukgwa/static_src/images/placeholder.webp
To: app/static/assets/images/placeholder.webp
```

#### Sprites (if used)

- Review `sprites/sprites.html` to see if SVG sprites are needed
- May be handled by TNA Frontend library

### 5. Build System Updates

#### package.json Updates

```json
{
  "dependencies": {
    "@nationalarchives/frontend": "^0.30.2",
    "js-cookie": "^3.0.5",
    "lite-youtube-embed": "^0.3.4"
  },
  "devDependencies": {
    "@babel/core": "^7.22.11",
    "@babel/preset-env": "^7.22.10",
    "babel-loader": "^10.0.0",
    "sass": "^1.69.4",
    "terser-webpack-plugin": "^5.3.10",
    "webpack": "^5.88.2",
    "webpack-cli": "^6.0.1",
    "copy-webpack-plugin": "^11.0.0",
    "css-loader": "^6.8.1",
    "mini-css-extract-plugin": "^2.7.6",
    "postcss": "^8.4.31",
    "postcss-loader": "^7.3.3",
    "autoprefixer": "^10.4.16",
    "sass-loader": "^8.0.2"
  },
  "scripts": {
    "compile:css": "webpack --entry ./src/styles/main.scss --mode production",
    "compile:js": "webpack --entry ./src/scripts/main.js --mode production",
    "compile": "npm run compile:css && npm run compile:js",
    "dev:css": "webpack --entry ./src/styles/main.scss --mode development --watch",
    "dev:js": "webpack --entry ./src/scripts/main.js --mode development --watch",
    "dev": "npm run dev:css & npm run dev:js &"
  }
}
```

#### webpack.config.js Updates

- Combine approaches from both repositories
- Use webpack for both CSS and JS (unified build)
- Add SCSS loader configuration
- Add font and image handling
- **Exclude Tailwind** configuration
- Keep terser for JS minification

### 6. Context Processors / Template Globals

Create `app/lib/template_context.py` or similar to provide:

- Navigation data (primary, secondary, footer)
- Site settings (social media handles, etc.)
- Config values (Google Analytics, cookie domain)
- Helper functions previously in Django template tags

Example:

```python
@app.context_processor
def inject_navigation():
    return {
        'primary_nav': get_primary_navigation(),
        'secondary_nav': get_secondary_navigation(),
        'footer_nav': get_footer_navigation(),
        'footer_links': get_footer_links(),
    }

@app.context_processor
def inject_settings():
    return {
        'social_media': {
            'twitter_handle': app_config.TWITTER_HANDLE,
            'facebook_app_id': app_config.FACEBOOK_APP_ID,
        },
        'site_name': app_config.SITE_NAME,
    }
```

### 7. Custom Jinja2 Macros Needed

#### Icon Macro

```jinja2
{# macros/icon.html #}
{% macro icon(name, classname='', viewbox='0 0 24 24') %}
<svg class="icon {{ classname }}" viewBox="{{ viewbox }}" aria-hidden="true">
    <use href="#icon-{{ name }}"></use>
</svg>
{% endmacro %}
```

#### Responsive Image Macro

```jinja2
{# macros/responsive_image.html #}
{% macro responsive_image(src, alt, sizes='100vw', loading='lazy') %}
<img src="{{ src }}"
     alt="{{ alt }}"
     sizes="{{ sizes }}"
     loading="{{ loading }}"
     class="responsive-image">
{% endmacro %}
```

## Implementation Order

### Phase 1: Setup & Assets (Day 1)

1. ✅ Create merge plan document
2. Copy SCSS structure and files
3. Copy JavaScript components
4. Copy fonts and images
5. Update package.json with new dependencies

### Phase 2: Build System (Day 1-2)

6. Update webpack.config.js
7. Test CSS compilation
8. Test JS compilation
9. Verify asset paths in compiled files

### Phase 3: Base Templates (Day 2)

10. Convert base.html and base_page.html
11. Create context processors for common data
12. Test base template rendering

### Phase 4: Core Components (Day 2-3)

13. Convert header component
14. Convert footer component
15. Convert navigation components
16. Convert skip link and basic UI elements
17. Test component rendering

### Phase 5: Content Components (Day 3-4)

18. Convert card, hero, page header
19. Convert listing and pagination
20. Convert alert banners
21. Convert streamfield components
22. Create macros for reusable elements

### Phase 6: Page Templates (Day 4-5)

23. Convert home page template
24. Convert standard page templates
25. Convert error pages
26. Test all page templates

### Phase 7: Testing & Refinement (Day 5)

27. Visual regression testing
28. Cross-browser testing
29. Accessibility testing
30. Performance testing
31. Fix any issues found

## Files to Exclude

### DO NOT Copy

- `ukgwa/project_styleguide/templates/pattern_library/` - Pattern Library UI
- `ukgwa/project_styleguide/templates/_pattern_library_only/` - Pattern Library specific
- `*.yaml` files in template directories - Pattern Library data files
- `*.md` files - Documentation for Pattern Library
- Tailwind directives from CSS
- Django-specific Python files

## Testing Checklist

### Visual

- [ ] Header renders correctly
- [ ] Footer renders correctly
- [ ] Navigation menus work
- [ ] Cards display properly
- [ ] Hero sections look correct
- [ ] Typography matches design
- [ ] Colors and spacing correct
- [ ] Icons display properly

### Functional

- [ ] Mobile menu works
- [ ] Skip link functions
- [ ] YouTube consent manager works
- [ ] Table hints display
- [ ] Accordion components work
- [ ] Tabs function correctly
- [ ] Forms submit properly
- [ ] Links navigate correctly

### Cross-browser

- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers

### Accessibility

- [ ] Keyboard navigation
- [ ] Screen reader testing
- [ ] ARIA attributes correct
- [ ] Focus management
- [ ] Color contrast

### Performance

- [ ] CSS file size reasonable
- [ ] JS file size reasonable
- [ ] Assets load quickly
- [ ] No console errors

## Potential Issues & Solutions

### Issue 1: Wagtail Image Tags

**Problem**: `{% image page.image width-400 %}` won't work in Flask
**Solution**: Create a Jinja2 filter or macro that generates responsive image HTML with srcset

### Issue 2: Navigation Template Tags

**Problem**: `{% primary_nav %}` and similar custom tags don't exist
**Solution**: Create context processors that pass navigation data, use macros to render

### Issue 3: Settings Access

**Problem**: `{{ settings.core.SocialMediaSettings.twitter_handle }}`
**Solution**: Move to Flask config or database, expose via context processor

### Issue 4: Wagtail UserBar

**Problem**: `{% wagtailuserbar %}` for admin
**Solution**: Remove - not needed in Flask app

### Issue 5: Social Image Tags

**Problem**: Complex image processing in Django template
**Solution**: Implement image processing in Python view, pass URLs to template

### Issue 6: TypeScript Components

**Problem**: Some JS components are TypeScript
**Solution**: Either add TypeScript support to webpack or convert to JavaScript

### Issue 7: Pattern Library Context

**Problem**: Templates expect Pattern Library provided context
**Solution**: Ensure all context is provided from Flask views

## Success Criteria

- ✅ All SCSS files compile without errors
- ✅ All JavaScript files compile without errors
- ✅ Templates render without Jinja2 syntax errors
- ✅ Visual appearance matches wa-wagtail site
- ✅ All interactive components work
- ✅ No console errors in browser
- ✅ Accessibility maintained
- ✅ Build process is documented
- ✅ Development workflow is smooth

## Next Steps After Merge

1. Update documentation
2. Create component usage guide
3. Set up linting for templates
4. Create style guide page
5. Train team on new structure
6. Plan for ongoing maintenance

---

## Notes

- This is a significant migration requiring careful testing
- Maintain a checklist and test each component individually
- Keep original wa-wagtail repo for reference
- Consider doing merge in feature branch
- Review all converted templates with designer/frontend lead
- Document any deviations from original design

Generated: {{ now }}
