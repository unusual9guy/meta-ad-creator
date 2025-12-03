# Prompt Enhancement Plan
## Making Meta Ad Creatives Look Premium and Professional

### Current Issues
- Final product looks cheap/template-like
- Fonts are hardcoded (Calgary, RoxboroughCF, Tan Pearl)
- Text placement is restricted (only header/footer)
- Price tag is always included
- Prompts contain vague language that confuses the LLM
- Limited flexibility for modern, professional layouts

---

## Step-by-Step Enhancement Plan

### **Step 1: User-Provided Font System** 🎨
**Goal**: Allow users to input ANY font name directly, no restrictions or predefined lists

#### 1.1 Font Input UI
- **Action**: Add text input fields in Streamlit app for font names
- **Fields**:
  - **Primary Font** (for main text elements): Text input field
  - **Secondary Font** (optional, for additional text): Text input field
  - **Pricing Font** (if price enabled): Text input field
- **Implementation**: 
  - Simple text input fields (not dropdowns)
  - No validation against a predefined list
  - Accept any font name the user provides
  - Allow empty fields (will use defaults if needed)

#### 1.2 Update Prompt Generator
- **Remove**: All hardcoded font references (Calgary, Tan Pearl, RoxboroughCF)
- **Remove**: Font categories and restrictions
- **Add**: Dynamic font injection from user input
- **Critical**: Add explicit instructions to use EXACTLY the font name provided by user
- **No Validation**: Do NOT restrict or validate font names - accept whatever user provides

#### 1.3 Font Usage Instructions in Prompt
- **Clear directive**: "Use EXACTLY the font name specified in the 'font' field. The font name is: [USER_PROVIDED_FONT_NAME]. Do NOT substitute, modify, use similar fonts, or use any other font. Use this exact font name only."
- **Example**: If user provides "MyCustomFont", the prompt must state: "Use the font named 'MyCustomFont' exactly as specified. Do not use any other font."
- **Multiple Fonts**: If user provides multiple fonts, use each for its designated purpose
- **No Fallback**: If font not provided, explicitly state "Use a clean, professional sans-serif font" rather than defaulting to a specific font name

---

### **Step 2: Company Logo Integration** 🏢
**Goal**: Allow users to upload company logo and place it strategically in the ad creative

#### 2.1 Logo Upload UI
- **Action**: Add file uploader in Streamlit app for company logo
- **Location**: Product details form (Step 2)
- **File Types**: PNG, JPG, JPEG, SVG (with transparency support preferred)
- **Optional**: Checkbox "Include Company Logo" (default: unchecked)
- **Preview**: Show logo preview after upload

#### 2.2 Logo Processing
- **Action**: Process uploaded logo image
- **Requirements**:
  - Maintain aspect ratio
  - Resize to appropriate size (suggest 150-200px width for 1080px canvas)
  - Preserve transparency if available
  - Save to temporary location for prompt generation

#### 2.3 Logo Placement in Prompt
- **Default Position**: Top-center or top-left (user preference)
- **JSON Structure**:
  ```json
  "branding": {
    "logo": {
      "enabled": true/false,
      "image_path": "[path to logo]",
      "placement": {
        "position": "top-left|top-center|top-right",
        "x_offset": 0,
        "y_offset": 20,
        "size": "small|medium|large"
      },
      "style": {
        "opacity": 1.0,
        "background": "transparent|white|none"
      }
    }
  }
  ```
- **Instructions**: "Place the company logo at the top of the image. Logo should be clearly visible but not overpower the product. Maintain logo's original colors and design. Do not modify, distort, or redesign the logo."

#### 2.4 Layout Adjustments with Logo
- **With Logo**: Adjust text elements to avoid overlap with logo
- **Product Positioning**: May need slight adjustment if logo takes top space
- **Visual Hierarchy**: Logo → Product → Text elements

---

### **Step 3: Price Tag Toggle** 💰
**Goal**: Give users option to include or exclude pricing information

#### 3.1 UI Implementation
- **Action**: Add checkbox/toggle in Streamlit app: "Include Price Tag"
- **Default**: Checked (include price)
- **Location**: Product details form (Step 2)

#### 3.2 Prompt Logic Update
- **Conditional JSON Structure**:
  - If price enabled: Include full `pricing_display` and `limited_time_offer` sections
  - If price disabled: Remove these sections entirely from JSON
  - Update `typography_and_layout.style` to reflect price inclusion status

#### 3.3 Layout Adjustments
- **With Price**: Maintain current layout with pricing badge in bottom-right
- **Without Price**: Redistribute text elements for better visual balance
  - Headline can be larger/more prominent
  - Footer can be repositioned
  - More space for product showcase

---

### **Step 4: Flexible Text Placement** 📍
**Goal**: Allow text elements anywhere in the composition, not just header/footer

#### 4.1 New JSON Structure (Based on Example Analysis)
- **Replace**: Fixed "headline" and "footer" structure
- **Add**: Flexible `text_elements` array with support for multiple element types:
  ```json
  "text_elements": [
    {
      "type": "text",
      "text": "...",
      "font": "[USER_PROVIDED_FONT_NAME]",
      "placement": {
        "position": "top-left|top-center|top-right|center-left|center|center-right|bottom-left|bottom-center|bottom-right|custom",
        "x_offset": 0,
        "y_offset": 0,
        "alignment": "left|center|right"
      },
      "style": {
        "size": "small|medium|large|xlarge",
        "weight": "light|regular|bold",
        "color": "#hexcode",
        "transform": "none|uppercase|lowercase|capitalize"
      },
      "hierarchy": "primary|secondary|tertiary"
    },
    {
      "type": "features",
      "items": [
        {"icon": "icon_name", "text": "Feature text"},
        {"icon": "icon_name", "text": "Feature text"}
      ],
      "placement": {"position": "bottom", "y_offset": -120},
      "style": {"layout": "horizontal|vertical", "spacing": "even"}
    },
    {
      "type": "cta_button",
      "text": "SHOP NOW",
      "placement": {"position": "bottom-center", "y_offset": -40},
      "style": {
        "background_color": "#hexcode",
        "text_color": "#hexcode",
        "border_radius": 8,
        "padding": "12px 32px"
      }
    }
  ]
  ```
- **Key Points**:
  - Support for text, features (with icons), and CTA buttons
  - Font field uses EXACTLY what user provides
  - Multiple text elements allowed anywhere
  - AI can suggest optimal placement based on product analysis
  - Based on real-world ad examples (serving dish, cutlery holder, brush stand)

#### 4.2 AI-Driven Layout Suggestions
- **Action**: Let the prompt generator analyze the product image and suggest optimal text placements
- **Considerations**:
  - Product shape and orientation
  - Empty spaces in composition
  - Visual hierarchy principles
  - Modern advertising trends
  - Strategic placement for maximum impact (not restricted to top/bottom)

#### 4.3 Flexible Text Elements
- **Allow**: Any number of text elements (suggest max 5-6 for clarity)
- **No Restrictions**: Text can be placed:
  - Over the product (if it enhances the design)
  - In negative space
  - As overlay elements
  - In corners, sides, or center
  - Anywhere that creates a professional, modern layout
- **Priority**: Assign visual hierarchy (primary, secondary, tertiary) based on importance, not position

---

### **Step 5: Reference Examples Analysis** 📸
**Goal**: Study example images to understand desired aesthetic

#### 5.1 Example Image Review
- **Location**: `example_images/` folder
- **Images analyzed**:
  - WhatsApp Image 2025-12-03 at 13.59.57_c36a2f1d.jpg (Serving Dish)
  - WhatsApp Image 2025-12-03 at 13.59.57_e92ff427.jpg (Cutlery Holder)
  - WhatsApp Image 2025-12-03 at 13.59.53_b0c4d0e1.jpg (Brush Stand)

#### 5.2 Extract Design Patterns from Examples

**Pattern 1: Strategic Text Placement**
- **Top-center titles**: "Elegant", "Ordinary dining is calling?", "Add Timeless Elegance"
- **Taglines below titles**: "Serve Beautifully", "Let opulence answer instead"
- **Product names at bottom**: "Mother of Pearl Designer Duo Cutlery Holder"
- **Body text in middle section**: Feature descriptions, product benefits
- **Text NOT restricted to edges**: Can be placed anywhere for visual balance

**Pattern 2: Feature Icons with Text**
- **Visual elements**: Icons representing product features
- **Layout**: Icons with descriptive text below (e.g., "Stylish Design", "Versatile", "Durable Build")
- **Placement**: Bottom section, arranged horizontally
- **Style**: Simple line-art icons, clean and minimal

**Pattern 3: Call-to-Action Buttons**
- **Prominent buttons**: "Shop The Collection", "SHOP NOW"
- **Styling**: Rounded corners, contrasting colors (tan/brown backgrounds with dark text)
- **Placement**: Bottom center or bottom section
- **Size**: Large enough to be clickable, but not overwhelming

**Pattern 4: Creative Visual Metaphors**
- **Call interface buttons**: Red "decline" and green "answer" buttons (cutlery holder ad)
- **Metaphorical messaging**: "Ordinary dining is calling? Let opulence answer instead"
- **Interactive elements**: Buttons that tell a story

**Pattern 5: Brand Logo Integration**
- **Top placement**: Logo at top-center when present
- **Brand name + tagline**: "CHITRA GOENKA" with "CRAFTS & CREATIONS"
- **Icon integration**: Stylized icons above brand name
- **Color coordination**: Logo colors match overall palette

**Pattern 6: Product Positioning**
- **Off-center placement**: Products often positioned to the right or left, not dead center
- **Vertical positioning**: Products at 45-60% from top (not centered vertically)
- **Size**: Products occupy 60-70% of canvas height
- **Subtle elevation**: Products appear slightly elevated with soft shadows

**Pattern 7: Background Styles**
- **Solid neutral colors**: Light beige (#F5F5DC), light brown (#D2B48C), off-white
- **OR blurred natural settings**: Soft depth of field, dining table, lifestyle context
- **No patterns or textures**: Clean, minimal backgrounds
- **Color coordination**: Background complements product colors

**Pattern 8: Typography Hierarchy**
- **Headlines**: Large serif fonts (48-72px), dark brown/gray (#2C2C2C)
- **Taglines**: Medium serif fonts (32-40px), same color as headline
- **Body text**: Smaller sans-serif fonts (20-28px), readable but secondary
- **Product names**: Medium serif fonts, positioned at bottom
- **CTAs**: Bold sans-serif on buttons, white text on dark backgrounds

**Pattern 9: Discount Integration**
- **In headline**: "Now 51% Off" integrated into main headline
- **Not separate badge**: Discount is part of the message, not isolated
- **Emphasis**: Discount text may be slightly larger or bold

**Pattern 10: Multiple Text Elements**
- **3-5 text elements**: Headline, tagline, body text, features, CTA
- **Clear hierarchy**: Primary (headline) → Secondary (tagline/body) → Tertiary (features/CTA)
- **Strategic spacing**: Elements don't crowd each other
- **Visual flow**: Top to bottom reading pattern

#### 5.3 Incorporate Learnings into Prompt

**New JSON Structure Based on Examples:**
```json
{
  "text_elements": [
    {
      "text": "Elegant",
      "font": "[USER_FONT]",
      "placement": {"position": "top-center", "y_offset": 80},
      "style": {"size": "xlarge", "weight": "bold", "color": "#2C2C2C"},
      "hierarchy": "primary"
    },
    {
      "text": "Serve Beautifully",
      "font": "[USER_FONT]",
      "placement": {"position": "top-center", "y_offset": 140},
      "style": {"size": "large", "weight": "regular", "color": "#2C2C2C"},
      "hierarchy": "secondary"
    },
    {
      "type": "features",
      "items": [
        {"icon": "dish_outline", "text": "Stylish Design"},
        {"icon": "floral_pattern", "text": "Versatile"},
        {"icon": "shield", "text": "Durable Build"},
        {"icon": "bowl", "text": "Integrated Bowl"}
      ],
      "placement": {"position": "bottom", "y_offset": -120},
      "style": {"layout": "horizontal", "spacing": "even"}
    },
    {
      "type": "cta_button",
      "text": "Shop The Collection",
      "placement": {"position": "bottom-center", "y_offset": -40},
      "style": {
        "background_color": "#D2B48C",
        "text_color": "#2C2C2C",
        "border_radius": 8,
        "padding": "12px 32px"
      }
    }
  ]
}
```

**Prompt Instructions Based on Examples:**
- "Create text elements similar to professional product advertisements: headline at top-center, tagline below, features/icons at bottom, CTA button at bottom-center"
- "Use solid neutral backgrounds (light beige #F5F5DC, light brown #D2B48C) OR blurred natural settings with soft depth of field"
- "Position product off-center (60% from left or right), at 50% from top, occupying 65% of canvas height"
- "Apply soft, even lighting with subtle shadows beneath product (5-10px blur, 20% opacity)"
- "Create feature icons with text: simple line-art style, arranged horizontally at bottom section"
- "Design CTA button: rounded corners, contrasting background color, centered at bottom, large enough to be prominent"
- "Integrate discount into headline if provided: 'Now [X]% Off' as part of main headline text"

---

### **Step 6: Refine Prompt Language** ✍️
**Goal**: Remove vague language, make instructions precise and actionable

#### 6.1 Identify Vague Terms
**Current vague phrases to replace**:
- ❌ "High-end professional photoshoot" → ✅ "Professional product photography with soft natural lighting, subtle shadows, and realistic depth of field"
- ❌ "Premium luxury brand aesthetic" → ✅ "Clean, sophisticated design with minimal text, natural backgrounds, and elegant typography"
- ❌ "Avoid generic Canva template" → ✅ "Do not use: flat backgrounds, bright saturated colors, heavy drop shadows, decorative borders, or template-style layouts"
- ❌ "Professional editing" → ✅ "Apply subtle color grading, soft shadows, natural highlights, and realistic depth of field blur"

#### 6.2 Add Specific Technical Instructions (Based on Examples)

- **Background** (Based on Example Analysis):
  - **Option 1 - Solid Neutral**: "Create a solid background in light beige (#F5F5DC), light brown (#D2B48C), or off-white. No patterns, textures, or gradients. Clean, minimal, professional."
  - **Option 2 - Blurred Natural**: "Create a blurred natural setting (dining table, vanity, lifestyle context) with soft depth of field. Background should be 40-50% blurred, maintaining context but keeping focus on product. Use warm, soft lighting."
  - "Background color should complement product colors: if product is warm-toned, use warm background; if cool-toned, use cool background"
  
- **Typography** (Based on Example Analysis):
  - **Headlines**: "Place headline at top-center, 80px from top. Use font size 48-72px (relative to 1080px canvas). Color: #2C2C2C (dark brown/gray). Weight: bold. Font: [USER_PROVIDED_FONT]"
  - **Taglines**: "Place tagline below headline, 140px from top. Use font size 32-40px. Color: #2C2C2C. Weight: regular. Font: [USER_PROVIDED_FONT]"
  - **Body Text**: "Place body text in middle section, 400-500px from top. Use font size 20-28px. Color: #2C2C2C. Weight: regular. Font: [USER_PROVIDED_FONT]"
  - **Product Names**: "Place product name at bottom, 200px from bottom. Use font size 28-36px. Color: #2C2C2C. Weight: regular. Font: [USER_PROVIDED_FONT]"
  - **CTA Buttons**: "Place CTA button at bottom-center, 40px from bottom. Button text: white (#FFFFFF) on dark background (#2C2C2C or #D2B48C). Font size: 18-24px. Border radius: 8px. Padding: 12px 32px"
  
- **Product Positioning** (Based on Example Analysis):
  - "Position product off-center: 60% from left OR 40% from left (not centered). Vertical position: 50% from top. Product should occupy 65% of canvas height (700px for 1080px canvas)"
  - "Maintain product original colors: do not adjust saturation, hue, or brightness"
  - "Add subtle shadow beneath product: soft, diffused, 5-10px blur, 20% opacity, offset 3-5px downward"
  - "Product should appear slightly elevated, not flat on background"
  
- **Feature Icons** (Based on Example Analysis):
  - "Create 3-5 feature items with simple line-art icons and descriptive text"
  - "Arrange features horizontally at bottom section, 120px from bottom"
  - "Icons: simple, clean line-art style (dish outline, floral pattern, shield, bowl, etc.)"
  - "Icon size: 40-50px. Text below icon: 16-20px font size"
  - "Spacing: even distribution across width, 10% margin from edges"
  
- **Layout Principles** (Based on Example Analysis):
  - "Follow top-to-bottom hierarchy: Logo (if present) → Headline → Tagline → Body Text → Product → Features → CTA Button"
  - "Maintain 10% margin from all edges for text elements"
  - "Ensure text doesn't overlap with product (unless intentional design choice)"
  - "Use negative space strategically: don't overcrowd, allow breathing room"

#### 6.3 Remove Redundancy
- **Consolidate**: Multiple mentions of "premium", "luxury", "professional"
- **Focus**: One clear definition per concept
- **Structure**: Use bullet points for clarity

#### 6.4 Add Negative Instructions
- **Explicitly forbid**:
  - "Do NOT use: gradients, patterns, geometric shapes, or decorative elements in background"
  - "Do NOT apply: filters, color overlays, or artistic effects to the product"
  - "Do NOT add: borders, frames, or decorative elements around text"
  - "Do NOT use: bright neon colors, high contrast, or saturated backgrounds"

---

## Implementation Priority

### Phase 1: Critical Fixes (Week 1)
1. ✅ Remove vague language from prompts
2. ✅ Add specific technical instructions
3. ✅ Implement user-provided font system
4. ✅ Add company logo upload and placement
5. ✅ Add price tag toggle

### Phase 2: Enhanced Features (Week 2)
6. ✅ Implement flexible text placement (text, features, CTA buttons)
7. ✅ Analyze example images (COMPLETED - 3 examples analyzed)
8. ✅ Update prompts with example-based learnings
9. ✅ Add feature icons support
10. ✅ Add CTA button styling
11. ✅ Implement example-based layout suggestions

### Phase 3: Refinement (Week 3)
10. ✅ Test with various products and logos
11. ✅ Refine based on output quality
12. ✅ Test logo placement variations
13. ✅ Optimize prompt length and clarity

---

## Success Metrics

### Quality Indicators
- ✅ Output looks like professional product photography (not AI-generated)
- ✅ Text placement is strategic and modern (not template-like)
- ✅ Fonts are correctly applied (no hallucination)
- ✅ Backgrounds are natural and realistic
- ✅ Overall composition is balanced and premium-looking

### Technical Validation
- ✅ Font names match user selection exactly
- ✅ Price tag appears/disappears based on toggle
- ✅ Text elements can be placed in various positions
- ✅ Prompt generates valid JSON without errors
- ✅ No vague terms in final prompt

---

## Files to Modify

1. **`src/agents/prompt_generator.py`**
   - Update system prompt
   - Accept user-provided font names (any font name)
   - Add logo image handling and placement instructions
   - Add price toggle parameter
   - Update JSON structure for flexible text placement (no headline/footer restrictions)
   - Add branding section for logo
   - Remove all hardcoded font references

2. **`src/app.py`**
   - Add font input fields (text inputs, not dropdowns):
     - Primary Font (required)
     - Secondary Font (optional)
     - Pricing Font (optional, shown if price enabled)
   - Add logo uploader with preview
   - Add "Include Company Logo" checkbox
   - Add price toggle checkbox
   - Pass font names, logo, and price toggle to prompt generator
   - Update prompt review section to show flexible text elements and logo placement

3. **`docs/prompt_examples.md`** (NEW)
   - Document example image analysis
   - Include design pattern references
   - Add prompt templates for different styles
   - Note: No font config file needed - users provide fonts directly

---

## Next Steps

1. **Review this plan** and confirm approach
2. **Analyze example images** in `data/input/` folder
3. **Update prompt_generator.py** with refined prompts (accept any font name, handle logo)
4. **Update app.py** with:
   - Font input fields (text inputs, not dropdowns)
   - Logo uploader with preview
   - Logo placement options
5. **Test with various font names** (including custom/uncommon fonts)
6. **Test logo placement** with different logo sizes and formats
7. **Iterate based on output quality**

---

## Notes

- Keep prompts under 2000 tokens to avoid truncation
- Use clear, actionable language (avoid marketing jargon)
- Test each change incrementally
- **Font Handling**: Accept ANY font name from user - do not restrict or validate
- **Font Instructions**: Be very explicit in prompt: "Use EXACTLY the font named '[USER_FONT]' - do not substitute"
- **No Font Config**: Users provide fonts directly - no predefined list needed
- **Flexible Text**: No restrictions on text placement - allow modern, strategic layouts
- **Logo Handling**: 
  - Accept logo in common formats (PNG, JPG, SVG)
  - Preserve transparency for PNG logos
  - Default placement: top-center or top-left
  - Logo should not overpower product
  - Maintain logo's original design and colors
- Consider adding helper text in UI: "Enter the exact font name you want to use"
- Logo preview in UI before generating creative

