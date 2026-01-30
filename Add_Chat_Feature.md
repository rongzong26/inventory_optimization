# Adding AI Chat Feature to Inventory App

This guide shows how to integrate Genie chat into your inventory optimization app.

---

## 🎯 Two Integration Options

### Option 1: Link to Genie Space (Easiest)
Add a button that opens Genie in a new tab

### Option 2: Embedded Chat Widget (Advanced)
Embed Genie directly in the app interface

---

## 📋 Step 1: Create Genie Space

**Instructions:**

1. **Go to Genie in your workspace:**
   - URL: https://fe-sandbox-serverless-v7m02q.cloud.databricks.com/genie
   - Or click **"Genie"** in left sidebar

2. **Create New Space:**
   - Click **"Create Genie Space"** or **"New"**
   - **Name:** "Inventory Optimization Assistant"
   - **Description:** "Ask questions about spare parts inventory across mine sites"

3. **Add Data:**
   - Click **"Add data sources"**
   - Select: **`rz-demo-mining.supply-chain.gold_master_part_inventory`**
   - Click **"Add"**

4. **Configure (Optional):**
   Add instructions for better context:
   ```
   This space helps analyze spare parts inventory across mining sites.
   
   Key columns:
   - plant_name: Mine site location
   - part_name: Spare part type
   - risk_level: Stock status (Stocked, Low Stock, Out of Stock)
   - on_hand_stock: Current inventory quantity
   - safety_stock: Minimum required quantity
   - shortage_quantity: Additional parts needed
   - work_order_id: Planned maintenance requiring parts
   ```

5. **Save and Get URL:**
   - Click **"Create"**
   - Copy the URL from your browser (looks like: `.../genie/rooms/xxxxx`)

---

## 📋 Step 2: Integrate into App

Once you have the Genie space URL, I'll add:

### A. Chat Button in App Header
- Button labeled "AI Chat Assistant" or "Ask Questions"
- Opens Genie space in new tab

### B. Embedded Chat Panel (Optional)
- Side panel with Genie iframe
- Toggle to show/hide

### C. Context-Aware Links
- When user selects a site/part, link to pre-filtered Genie questions
- Example: "Ask AI about Brisbane Mine inventory"

---

## 🎨 Design Options

### Minimal Integration:
```
+----------------------------------+
| Inventory App         [AI Chat] |  <- Button in header
+----------------------------------+
| Map | Filters | Data            |
+----------------------------------+
```

### Full Integration:
```
+----------------------------------------+
| Inventory App    [Toggle Chat Panel]  |
+----------------------------------------+
| Map & Data        | [Genie Chat]      |
| +--------------+  | [User: Show      |
| | Mine Sites   |  |  low stock]      |
| |              |  |                   |
| |   [Graph]    |  | [AI: Here are    |
| |              |  |  3 sites with    |
| +--------------+  |  low stock...]   |
+----------------------------------------+
```

---

## 🔧 Code Changes Required

I'll modify these files:
1. **`app/layout.py`** - Add chat button/panel to UI
2. **`app/app.py`** - Add callback to handle chat interactions
3. **`databricks.yml`** - No changes needed

---

## 📝 Sample Genie Questions

Once integrated, users can ask:

**Inventory Status:**
- "Which sites have parts out of stock?"
- "Show me all low stock items"
- "What parts are below safety stock?"

**Site Analysis:**
- "What's the inventory status at Brisbane Mine?"
- "Compare inventory levels across all sites"
- "Which site has the most stockout risks?"

**Part Tracking:**
- "Where can I find Hydraulic Pumps?"
- "Show me Conveyor Belt inventory across sites"
- "Which parts have the highest shortage quantities?"

**Recommendations:**
- "What should I order for Melbourne Mine?"
- "Which sites can transfer parts to Perth Mine?"
- "Show upcoming maintenance that might cause shortages"

**Trends & Analytics:**
- "What's the average on-hand stock per site?"
- "Which equipment types have the most critical parts?"
- "Show me the distribution of risk levels"

---

## 🚀 Next Steps

**Provide me with:**
1. Your Genie space URL (after creating it)
2. Which integration option you prefer:
   - [ ] Simple button link
   - [ ] Embedded chat panel
   - [ ] Both

Then I'll:
1. Update the app code to integrate Genie
2. Add the chat button/panel
3. Deploy the updated app
4. Test the integration

---

## 💡 Pro Tips

**For Better Genie Responses:**
1. Add raw tables too (raw_parts, raw_plants, etc.) for detailed queries
2. Configure instructions with business context
3. Add example questions in the space
4. Set up a sample conversation to train users

**For App Integration:**
1. Start with simple link button
2. Test with users
3. Add embedded chat if needed based on feedback
4. Consider mobile responsiveness

---

## ⚠️ Important Notes

- Genie requires users to have access to the underlying tables
- Users need appropriate workspace permissions
- Genie is available in workspaces with SQL warehouse access
- Response quality improves with better table documentation

---

**Ready to integrate? Create the Genie space and share the URL!** 🚀
