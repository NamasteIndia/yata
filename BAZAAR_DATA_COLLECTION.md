# Bazaar/Market Data Collection in YATA

**Last Updated:** 2026-02-18  
**Purpose:** Document how YATA collects, processes, and maintains market/bazaar data from Torn City

---

## Overview

YATA collects bazaar/market data through **three main mechanisms**:

1. **Scheduled Cron Jobs** - Automated periodic updates from Torn City API
2. **User-Initiated Updates** - Real-time updates when users view specific items
3. **Third-Party Client Submissions** - External tools submitting foreign stock data

---

## 1. Scheduled Cron Jobs

### Item Metadata Updates (`items` command)

**File:** `bazaar/management/commands/items.py`  
**Schedule:** Runs **twice daily** at 02:30 and 14:30 (crontab: `30 2,14 * * *`)

**What it does:**
1. **Fetches item catalog** from Torn API using two endpoints:
   - `torn/?selections=items,timestamp` - All items in Torn City
   - `market/?selections=pointsmarket` - Points market data

2. **Updates Item model** for each item:
   - Creates new items if they don't exist
   - Updates existing items with latest metadata:
     - `tName` - Item name
     - `tType` - Item type (weapon, drug, etc.)
     - `tMarketValue` - Current market value from Torn
     - `tSellPrice`, `tBuyPrice` - NPC prices
     - `tCirculation` - Total items in circulation
     - `tDescription`, `tEffect`, `tRequirement` - Item details
     - `tImage` - Image URL

3. **Calculates points value**:
   - Aggregates all points market items
   - Computes average $ per point: `total_price / total_points`
   - Stores in `BazaarData.pointsValue`

4. **Maintains price history**:
   - Each update adds timestamp and market value to `Item.priceHistory` JSON field
   - Keeps data for **31 days** (older entries deleted)
   - Rounds timestamps to the hour to reduce data points

5. **Computes price trends** via `updateTendencies()`:
   - **Week Tendency:** Linear regression on last 7 days of prices
   - **Month Tendency:** Linear regression on last 31 days of prices
   - Stores slope (`A`) and intercept (`B`) coefficients
   - Uses scipy's `stats.linregress()` for calculations

6. **Determines market activity**:
   - Item marked as `onMarket=True` if:
     - Has at least 10 price history entries
     - Last 10 entries all have prices > 0 (not out of stock)

7. **Cleanup tasks**:
   - Deletes market data for custom items not updated in 24h
   - Removes abroad stock entries older than 14 days (except last entry)
   - Updates `typeItem` and `itemType` JSON mappings

**Code snippet:**
```python
# From bazaar/management/commands/items.py
points = apiCall("market", "", "pointsmarket", randomKey(), sub="pointsmarket")
items = apiCall("torn", "", "items,timestamp", randomKey(), sub="items")

for k, v in items.items():
    req = Item.objects.filter(tId=int(k))
    if len(req) == 0:
        item = Item.create(k, v)  # Create new item
    else:
        item = req[0]
        item.update(v)  # Update existing item
    item.save()
```

---

## 2. User-Initiated Updates

### Real-Time Bazaar Price Updates

**File:** `bazaar/views.py` → `update()` function  
**Trigger:** When user clicks "Update" button on an item in the web interface  
**Method:** POST request to `/bazaar/update/<itemId>/`

**What it does:**
1. **Fetches live bazaar listings** from Torn API v2:
   - Endpoint: `market/{itemId}?selections=itemmarket` (v2)
   - Returns current listings with prices and quantities

2. **Processes listings**:
   - Groups consecutive items at same price
   - Example: 5 items at $1000, 3 at $1200 → 2 market data entries
   - Sorts by price (lowest first)

3. **Updates MarketData model**:
   - Deletes old entries: `item.marketdata_set.all().delete()`
   - Creates new entries for each price point
   - Limits to `n` entries (default 10, configurable via `BazaarData.nItems`)
   - Each entry stores:
     - `cost` - Price per item
     - `quantity` - Number of items at this price
     - `itemmarket` - Always True (from itemmarket endpoint)

4. **Updates Item timestamp**:
   - Sets `item.lastUpdateTS` to current timestamp
   - Used to show how "fresh" the data is in UI

**Code snippet:**
```python
# From bazaar/models.py - Item.update_bazaar()
def update_bazaar(self, key="", n=10):
    req = apiCall("market", self.tId, "itemmarket", key, v2=True)
    itemmarket = req.get("itemmarket", {})
    
    # Group by price
    marketData = []
    pp = 0  # previous price
    q = 0   # quantity
    for i, v in enumerate(itemmarket["listings"]):
        if v["price"] == pp:
            q += 1
        else:
            if i: marketData.append({"cost": pp, "quantity": q, "itemmarket": True})
            q = 1
            pp = v["price"]
    
    # Delete old and create new
    self.marketdata_set.all().delete()
    for i, v in enumerate(marketData):
        self.marketdata_set.create(**v)
        if i >= n - 1:
            break
```

---

## 3. Foreign Stock Data (Third-Party Submissions)

### API Endpoint for External Clients

**File:** `api/views/travel.py` → `importStocks()` function  
**Endpoint:** POST to `/api/v1/travel/import/`  
**Schedule:** External tools submit data when users travel abroad

**What it does:**

#### Data Submission Flow:
1. **Third-party clients** (browser extensions, scripts) detect when user is abroad
2. **Extract stock data** from Torn City's foreign stock pages
3. **Submit payload** to YATA API:
```json
{
  "country": "jap",
  "items": [
    {"id": 197, "quantity": 152, "cost": 25000},
    {"id": 198, "quantity": 89, "cost": 12000}
  ],
  "client": "TornTools",
  "version": "5.2.1",
  "uid": 2000607
}
```

#### Server Processing:
1. **Validates payload**:
   - Checks required keys: `country`, `items`
   - Verifies country code is valid (mex, cay, can, haw, uni, arg, swi, jap, chi, uae, sou)
   - Ensures all item IDs, costs, quantities are integers

2. **Rate limiting**:
   - Cache lock per country: 60-second cooldown
   - Prevents duplicate submissions within 60s

3. **Client verification**:
   - Checks if client is in `VerifiedClient` list
   - Only verified clients can update the database
   - Unverified clients get response but don't update DB

4. **Data normalization**:
   - Converts items to dict format if submitted as list
   - Casts all IDs to integers
   - Validates against `items_table` (whitelist of items per country)

5. **Stock updates**:
   - Marks old stocks as `last=False`
   - Creates new `AbroadStocks` entries with `last=True`
   - Stores:
     - Item reference
     - Country code and name
     - Cost and quantity
     - Timestamp
     - Client name and version

6. **Cache invalidation**:
   - Deletes `foreign_stocks_payload` cache
   - Forces next export request to rebuild from database

**Code snippet:**
```python
# From api/views/travel.py - importStocks()
client, _ = VerifiedClient.objects.get_or_create(name=client_name, version=client_version)
if client.verified:
    for k, v in stocks.items():
        item = Item.objects.filter(tId=k).first()
        AbroadStocks.objects.filter(item=item, country_key=v["country_key"], last=True).update(last=False)
        v["last"] = True
        item.abroadstocks_set.create(**v)  # Create new stock entry
    cache.delete("foreign_stocks_payload")  # Invalidate cache
```

### Foreign Stock Export API

**File:** `api/views/travel.py` → `exportStocks()` function  
**Endpoint:** GET `/api/v1/travel/export/`  
**Purpose:** Provide aggregated foreign stock data to clients

**What it does:**
1. **Checks cache first**:
   - Key: `foreign_stocks_payload`
   - TTL: 1 hour (3600 seconds)
   - Returns cached data if available

2. **Builds payload** (if cache miss):
   - Queries `AbroadStocks.objects.filter(last=True)` (only latest entries)
   - Groups by country (11 countries)
   - For each country:
     - Gets update timestamp from most recent stock
     - Creates light payload for each stock (ID, name, quantity, cost)
   - Returns JSON:
```json
{
  "stocks": {
    "jap": {
      "update": 1708245600,
      "stocks": [
        {"id": 197, "name": "Erotic DVD", "quantity": 152, "cost": 25000},
        ...
      ]
    },
    ...
  },
  "timestamp": 1708245723
}
```

3. **Caches result** for 1 hour to reduce database load

---

## 4. Cron Job Details

### Items Images (`items_images` command)

**Schedule:** Daily at 00:00 (crontab: `0 0 * * *`)  
**File:** `bazaar/management/commands/items_images.py`  
**Purpose:** Downloads and caches item images locally (implementation not shown in files reviewed)

### Foreign Stocks Clients (`fstocks_clients` command)

**Schedule:** Twice daily at 02:35 and 14:35 (crontab: `35 2,14 * * *`)  
**File:** `bazaar/management/commands/fstocks_clients.py`  
**Purpose:** 
- Aggregates statistics about which clients are submitting data
- Calculates contribution percentages
- Stores in `BazaarData.clientsStats` JSON field

**Code snippet:**
```python
stocks = AbroadStocks.objects.all()
clients = {}
for stock in stocks:
    client_name = stock.client.split("[")[0].strip()
    if client_name not in clients:
        client = VerifiedClient.objects.filter(name=client_name).first()
        clients[client_name] = [0.0, client.author_id, client.author_name]
    clients[client_name][0] += 1.0 / float(max(1, len(stocks)))
```

### Foreign Stocks Cache Clear (`fstocks_clear_cache` command)

**Schedule:** **Every minute** (crontab: `* * * * *`)  
**File:** `bazaar/management/commands/fstocks_clear_cache.py`  
**Purpose:** Clears the foreign stocks export cache to ensure fresh data (likely with additional logic not shown)

### Foreign Stocks Clean (`fstocks_clean` command)

**Schedule:** Not in crontab (manual/on-demand)  
**File:** `bazaar/management/commands/fstocks_clean.py`  
**Purpose:** Cleanup old or duplicate foreign stock entries

---

## Data Models

### Item Model

**File:** `bazaar/models.py`

```python
class Item(models.Model):
    # Torn City data
    tId = models.IntegerField(unique=True)  # Torn item ID
    tName = models.CharField(max_length=200)
    tType = models.CharField(max_length=200)
    tMarketValue = models.BigIntegerField(default=0)  # Current market value from Torn
    tSellPrice = models.BigIntegerField(default=0)    # NPC sell price
    tBuyPrice = models.BigIntegerField(default=0)     # NPC buy price
    tCirculation = models.BigIntegerField(default=0)  # Total in circulation
    
    # YATA computed fields
    onMarket = models.BooleanField(default=False)     # Active on market?
    lastUpdateTS = models.IntegerField(default=0)     # Last bazaar update
    priceHistory = models.TextField(default={})        # JSON: {timestamp: price}
    
    # Price trend analysis (linear regression)
    weekTendency = models.FloatField(default=0.0)      # 7-day trend
    weekTendencyA = models.FloatField(default=0.0)     # Slope ($/second)
    weekTendencyB = models.FloatField(default=0.0)     # Intercept
    monthTendency = models.FloatField(default=0.0)     # 31-day trend
    monthTendencyA = models.FloatField(default=0.0)    # Slope
    monthTendencyB = models.FloatField(default=0.0)    # Intercept
    
    # Stock tracking
    stock = models.IntegerField(default=0)             # Total stock (computed)
    stockI = models.IntegerField(default=0)            # In inventory
    stockD = models.IntegerField(default=0)            # In display cabinet
    stockB = models.IntegerField(default=0)            # In bazaar
    
    # Foreign stocks
    seenAbroad = models.BooleanField(default=False)
    lastSeenAbroad = models.IntegerField(default=0)
```

### MarketData Model

**File:** `bazaar/models.py`

```python
class MarketData(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.BigIntegerField(default=1)      # Items at this price
    cost = models.BigIntegerField(default=0)          # Price per item
    itemmarket = models.BooleanField(default=False)   # From itemmarket endpoint
```

**Relationship:** One Item has many MarketData entries (one per price point)

### AbroadStocks Model

**File:** `bazaar/models.py`

```python
class AbroadStocks(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    
    country_key = models.CharField(default="???", max_length=3)  # e.g., "jap"
    country = models.CharField(max_length=32)                     # Full name
    quantity = models.IntegerField(default=0)
    cost = models.BigIntegerField(default=0)
    timestamp = models.IntegerField(default=0)
    
    client = models.CharField(default="unknown [0.0]", max_length=64)  # Submitting client
    last = models.BooleanField(default=True)  # Is this the latest entry?
```

**Relationship:** One Item has many AbroadStocks entries (one per country per update)

---

## API Integration Details

### Torn City API Calls

**Function:** `yata/handy.py` → `apiCall()`

**Usage in bazaar:**
1. **Item catalog:** `apiCall("torn", "", "items,timestamp", randomKey())`
2. **Points market:** `apiCall("market", "", "pointsmarket", randomKey())`
3. **Item bazaar:** `apiCall("market", itemId, "itemmarket", key, v2=True)`

**Features:**
- Random API key rotation via `randomKey()` from `setup.functions`
- Supports both v1 and v2 API endpoints
- Built-in caching with configurable TTL
- Error handling for API errors
- Automatic retry logic (implementation in handy.py)

---

## Price Trend Calculation

**Method:** Linear Regression using SciPy

**Algorithm (from `Item.updateTendencies()`):**

```python
from scipy import stats

# Week tendency (7 days)
x = []  # timestamps
y = []  # prices
for timestamp, price in priceHistory.items():
    if current_time - timestamp < 7 * 24 * 3600:  # Last 7 days
        if price > 0:
            x.append(timestamp)
            y.append(price)

if len(x) > 1:
    a, b, _, _, _ = stats.linregress(x, y)
    weekTendencyA = a  # Slope in $/second
    weekTendencyB = b  # Intercept
    weekTendency = a * 7 * 24 * 3600 / y[-1]  # Normalized tendency
```

**Interpretation:**
- `weekTendencyA` > 0: Price increasing
- `weekTendencyA` < 0: Price decreasing
- `weekTendency`: Percentage change over the period relative to current price
- Same logic applies for `monthTendency` but over 31 days

---

## Data Freshness & Caching

### Item Metadata
- **Update Frequency:** Twice daily (02:30, 14:30)
- **Data Age:** Up to 12 hours old
- **History Retention:** 31 days

### Bazaar Prices (MarketData)
- **Update Frequency:** On-demand by users
- **Data Age:** Shows `lastUpdateTS` in UI
- **Retention:** Deleted after 24h if item not on market

### Foreign Stocks
- **Update Frequency:** Real-time (as users travel)
- **Rate Limit:** 60s per country
- **Retention:** 48 hours (auto-cleanup)
- **Cache:** 1 hour on export endpoint

---

## User Inventory Tracking

**Method:** `player.getInventory()`  
**File:** `player/models.py`

When displaying items, YATA fetches user's inventory via:
- `user/?selections=inventory,bazaar,display`

This allows showing:
- `stockI`: Items in player inventory
- `stockB`: Items in player's bazaar
- `stockD`: Items in display cabinet
- `stock`: Total = I + B + D

**Used in views:**
```python
inventory = player.getInventory()
item.stockI = inventory.get("inventory", {}).get(str(item.tId), [0, 0])[0]
item.stockB = inventory.get("bazaar", {}).get(str(item.tId), [0, 0])[0]
item.stockD = inventory.get("display", {}).get(str(item.tId), [0, 0])[0]
item.stock = item.stockI + item.stockB + item.stockD
```

---

## Security & Verification

### Client Verification System

**Model:** `VerifiedClient`  
**Purpose:** Whitelist approved third-party tools

**Process:**
1. First submission creates unverified client
2. Admin manually verifies legitimate clients
3. Only verified clients update database
4. Prevents spam/malicious data

**Client Info Stored:**
- Name and version
- Author ID and name (from payload `uid`)
- Verification status
- Usage statistics

---

## Data Flow Diagram

```
┌─────────────────────┐
│   Torn City API     │
│  (items, market)    │
└──────────┬──────────┘
           │
           ├── Cron: items (2x/day)
           │   └─> Item.update()
           │       └─> updateTendencies()
           │           └─> Linear regression
           │
           ├── User clicks "Update"
           │   └─> Item.update_bazaar()
           │       └─> MarketData entries
           │
           └── Inventory fetch
               └─> player.getInventory()
                   └─> Stock quantities

┌─────────────────────┐
│  Third-Party Tools  │
│ (Browser extension) │
└──────────┬──────────┘
           │
           └── POST /api/v1/travel/import/
               └─> importStocks()
                   ├─> Validate payload
                   ├─> Check client verification
                   └─> AbroadStocks.create()
                       └─> Cache invalidation

┌─────────────────────┐
│   External Apps     │
│  (Mobile apps)      │
└──────────┬──────────┘
           │
           └── GET /api/v1/travel/export/
               └─> exportStocks()
                   ├─> Check cache (1h TTL)
                   └─> Query AbroadStocks
                       └─> Return JSON payload
```

---

## Performance Optimizations

### Caching Strategy
1. **Foreign stocks export**: 1-hour cache (reduces DB load)
2. **API responses**: Configurable cache per endpoint
3. **Rate limiting**: 60s locks per country for imports

### Database Optimization
1. **Indexing**: Unique index on `Item.tId`
2. **Filtering**: `last=True` for current foreign stocks
3. **Cleanup**: Auto-delete old data (24h, 48h, 14 days)
4. **Bulk operations**: Using Django's bulk update where applicable

### Data Size Management
1. **Price history**: Only 31 days retained
2. **Hourly rounding**: Reduces data points (24/day vs 1440/day)
3. **MarketData limit**: Configurable `n` entries (default 10)
4. **Abroad stocks**: Only latest per country kept with `last=True`

---

## Configuration

### BazaarData Model

**File:** `bazaar/models.py`

```python
class BazaarData(models.Model):
    nItems = models.IntegerField(default=10)              # Market data entries to keep
    lastScanTS = models.IntegerField(default=0)           # Last items cron run
    pointsValue = models.FloatField(default=10000)        # $/point ratio
    typeItem = models.TextField(default={})               # JSON: {type: [items]}
    itemType = models.TextField(default={})               # JSON: {item: type}
    clientsStats = models.TextField(default={})           # JSON: {client: [%, id, name]}
```

**Singleton pattern**: Only one instance exists, accessed via `.first()`

---

## Error Handling

### API Errors
- Checked via `"apiError" in response`
- Logged with `[CRON timestamp]` prefix
- Returns error dict to user if in view context

### Validation Errors
- Foreign stock imports validate all fields
- Returns 400 status with specific error message
- Examples:
  - Missing required keys
  - Invalid country code
  - Non-integer IDs/quantities/costs
  - Unknown item IDs

### Rate Limiting
- Cache-based locks prevent duplicate submissions
- Returns 200 with message (not 429) to avoid client retries

---

## Summary

YATA's bazaar data collection is a **multi-source, hybrid system**:

1. **Automated cron jobs** maintain item catalog and metadata twice daily
2. **User interactions** provide real-time bazaar price updates on-demand
3. **Third-party clients** crowdsource foreign stock data in real-time
4. **Linear regression** analyzes price trends over 7 and 31-day windows
5. **Caching** at multiple levels ensures performance at scale
6. **Verification system** maintains data quality from external sources

The system balances:
- **Freshness** (real-time user updates, crowd-sourced stocks)
- **Reliability** (scheduled updates, verified clients)
- **Performance** (caching, cleanup, rate limiting)
- **Accuracy** (statistical analysis, validation, API integration)

This architecture allows YATA to provide comprehensive market intelligence to Torn City players without overwhelming the Torn API or YATA's own infrastructure.
