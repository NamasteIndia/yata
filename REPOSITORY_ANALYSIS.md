# YATA Repository Analysis

**Generated:** 2026-02-18  
**Repository:** NamasteIndia/yata  
**Primary URL:** https://yata.yt/

---

## Executive Summary

YATA (Yet Another Torn App) is a comprehensive Django-based web application that serves as a helper/companion platform for Torn City (https://www.torn.com/), a text-based online RPG. The application integrates with Torn City's API to provide advanced analytics, market tracking, faction management, and combat coordination tools for players.

**Key Statistics:**
- **Total Files:** 9,609
- **Python Lines of Code:** ~41,900
- **JavaScript Files:** 61
- **HTML Templates:** 192
- **CSS Files:** 52
- **Django Apps:** 11 main applications
- **License:** GNU General Public License v3

---

## Technology Stack

### Backend
- **Framework:** Django 4.2.25
- **Python Version:** 3.8.10+
- **Database Support:** 
  - SQLite (default for development)
  - PostgreSQL (production)
- **Caching:** 
  - Django Database Cache (default)
  - Redis (optional, configurable)
- **Task Scheduling:** Custom cron system with schedule library
- **HTTP Server:** Gunicorn (production)

### Key Python Libraries
- **Data Processing:** NumPy, SciPy, scikit-learn, XGBoost
- **API Integration:** requests
- **Image Processing:** Pillow, python-magic
- **Security:** Sentry SDK for error tracking
- **Optimization:** 
  - django-htmlmin (HTML minification)
  - django-brotli (compression)
  - whitenoise (static file serving)
- **Development:** django-extensions, pre-commit hooks

### Frontend
- **Framework:** Server-rendered Django templates
- **Libraries:** jQuery, jQuery UI (1.12.1)
- **Styling:** Custom CSS
- **Static Files:** Managed with WhiteNoise

### Development Tools
- **Code Quality:** 
  - pre-commit hooks (black, flake8, isort, pyupgrade)
  - Line length: 200 characters
- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions (configured but currently backed up)

---

## Architecture Overview

### Django Applications (11 Apps)

#### 1. **player** (605 lines)
**Purpose:** Core player account management  
**Key Models:**
- `Player` - Main player profile with API keys, faction/company info, awards data
- `Key` - API key storage with access levels and validation
- `Message` - System-wide notifications
- `Donation`, `Error`, `TmpReq` - Supporting models

**Features:**
- API key management and validation
- Player statistics tracking
- Award/honor data aggregation
- Merit calculations
- Inventory management

#### 2. **faction** (4,887 lines - largest app)
**Purpose:** Faction/guild management and combat coordination  
**Key Features:**
- Member management and statistics
- Chain attack reports and coordination
- Attack/war planning tools
- Member targeting and assignments
- Data export functionality
- Configuration management

**Major Functionality:**
- ~20+ view functions
- Real-time chain coordination
- Member performance analytics
- Territory war management
- Attack report generation

#### 3. **bazaar** (398 lines)
**Purpose:** Item marketplace tracking and price analytics  
**Key Models:**
- `Item` - Market items with 7-day and monthly price trends using linear regression
- `MarketData` - Real-time market listings at different prices
- `BazaarData` - Aggregated market statistics
- `VerifiedClient` - Third-party client tracking
- `AbroadStocks` - Foreign country item availability

**Features:**
- Price history tracking
- Trend analysis and forecasting
- Custom item lists
- Market update monitoring
- Price charts and visualization

#### 4. **company** (513 lines)
**Purpose:** Player company/business management  
**Key Models:**
- `Company` - Company data (finances, employees, upgrades)
- `Employee` - Employee skills and effectiveness ratings
- `CompanyDescription`, `Position`, `Special`, `Stock` - Structure definitions
- `CompanyData`, `CompanyStock` - Historical performance tracking

**Features:**
- Company browsing and management
- Employee supervision
- Stock tracking
- Profit/performance analysis
- Efficiency calculations

#### 5. **target** (295 lines)
**Purpose:** Combat target tracking and attack logging  
**Key Models:**
- `Attack` - Detailed attack records with modifiers (fair fight, war, chain bonuses)
- `Revive` - Revive operations with success tracking
- `Target` - Target player profiles (status, faction, level, life)
- `TargetInfo` - Player-specific target notes and combat history

**Features:**
- Target list management
- Attack log analysis
- Loss tracking
- Revive coordination
- Data import/export

#### 6. **stock** (234 lines)
**Purpose:** Stock market tracking and investment analysis  
**Key Models:**
- `Stock` - Individual stocks with trend analysis (24h, 7-day, 4-month averages)
- `History` - Historical price/market cap data

**Features:**
- Price trend computation using linear regression
- Trigger system (below average prices, new shares, forecast changes)
- Stock filtering and sorting
- Price charts
- Investment recommendations

#### 7. **loot** (156 lines)
**Purpose:** NPC attack coordination for item drops  
**Key Models:**
- `NPC` - NPC tracking with hospitalization status and timing
- `ScheduledAttack` - Coordinated scheduled attacks

**Features:**
- Loot timing calculations
- Level progression tracking
- Attack scheduling
- NPC availability monitoring

#### 8. **awards** (74 lines)
**Purpose:** Achievement/medal tracking  
**Key Models:**
- `AwardsData` - Cache of available medals/honors with rarity scores

**Features:**
- Medal/honor tracking
- Rarity computation based on circulation
- Hall of fame
- Pin/unpin favorites
- Award calculations

#### 9. **api**
**Purpose:** RESTful API endpoints for external integrations  
**Key Features:**
- Faction data endpoints
- Stock market data
- Travel information
- Target data
- Authentication
- Spy reports
- Battle stats exchange (BSE)

#### 10. **setup**
**Purpose:** System configuration and API key setup  
**Key Models:**
- `APIKey` - Master API key storage with validation

**Features:**
- Key validation
- Random key selection for API calls
- System initialization

#### 11. **stocks** (406 lines - archived)
**Purpose:** Legacy stock market code (appears to be replaced by `stock` app)  
**Status:** Contains only commented-out model definitions

---

## Database Architecture

### Primary Database
- **Development:** SQLite3 (file-based)
- **Production:** PostgreSQL with connection pooling (600s max age)
- **ORM:** Django ORM with custom bulk operations

### Key Features
- Linear regression for trend analysis (stocks, bazaar prices)
- Scheduled task tracking
- Historical data aggregation
- API response caching

### Caching Strategy
- Database cache (default)
- Optional Redis cache for production
- Response caching (10 seconds default)
- Static file caching with WhiteNoise

---

## Cron Jobs & Background Tasks

### Task Management
- Custom cron system in `/cron/` directory
- Development runner: `dev_cron.py`
- Production: Standard crontab

### Scheduled Tasks (from crontab.txt)
- **Daily:**
  - API key validation (00:00)
  - Awards data refresh (00:05, 12:05)
  - Faction data sync (00:00, 12:00)
  - Player statistics (03:05, 15:05)
  - Company updates (07:00, 20:00 - around Torn update times)
  - Item images (00:00)
  - Bazaar data (02:30, 14:30)

- **Every Minute:**
  - Chain reports (5 parallel workers)
  - Attack reports (3 parallel workers)
  - Revive reports (2 parallel workers)
  - Armory updates (2 parallel workers)
  - Foreign stock cache clearing

### Task Execution
- Bash wrapper: `run_command.bash`
- Django management commands
- Parallel execution for high-frequency tasks

---

## API Integration

### Torn City API
The application heavily integrates with Torn City's API for:
- Player data retrieval
- Faction information
- Market/bazaar data
- Stock prices
- Combat logs
- NPC timing
- Award/honor data

### API Key Management
- Multiple key support with access levels
- Automatic key rotation
- Rate limiting with django-ratelimit
- Key validation and health checks

### External APIs Provided
- RESTful endpoints for third-party tools
- CORS enabled for cross-origin requests
- Client verification system
- Data export capabilities

---

## Security Features

### Authentication & Authorization
- Django's built-in auth system
- API key-based authentication
- Session management (signed cookies)
- CSRF protection

### Security Middleware
- XForwardedForMiddleware for proxy handling
- HTTPS enforcement (via proxy header)
- Clickjacking protection
- Content Security

### Error Tracking
- Optional Sentry integration
- Configurable sample rates
- Environment-specific tracking
- PII handling

### Code Quality
- Pre-commit hooks for security checks:
  - Private key detection
  - Large file prevention
  - Merge conflict detection
  - Syntax validation

---

## Configuration Management

### Environment Variables (.env)
**Required:**
- `DEBUG` - Debug mode toggle
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Allowed hostnames
- `LOG_KEY` - Logging key
- `ADMIN_URL_PREFIX` - Admin panel URL prefix
- `DATABASE` - Database backend selection

**Optional:**
- `CACHE_RESPONSE` - Cache duration
- `CHAIN_REPORT`, `ATTACK_REPORT`, `REVIVE_REPORT` - Cron job counts
- Redis configuration
- Sentry configuration
- PostgreSQL credentials

### Static Files
- **Collection:** WhiteNoise with compression
- **Storage:** Compressed static file storage
- **Directories:** 
  - Source: `yata/static/`
  - Collected: `yata/staticfiles/`
- **Assets:** Favicon, fonts, images, payloads, third-party libraries

### Media Files
- **URL:** `/media/`
- **Root:** `yata/media/`
- **Content:** User-generated content, cached images

---

## Development Workflow

### Setup Process
1. Clone repository
2. Install dependencies (`pip install -r requirements.txt`)
3. Create `.env` file with configuration
4. Run `python setup.py` to initialize
5. Start development server (`python manage.py runserver`)
6. Optional: Run dev cron (`python ./cron/dev_cron.py`)

### Pre-commit Hooks
Enforces code quality with:
- **black** - Code formatting (200 char line length)
- **flake8** - Linting
- **isort** - Import sorting
- **pyupgrade** - Python syntax modernization
- **autoflake** - Unused import removal
- Multiple file checks (merge conflicts, private keys, etc.)

### Testing
- Test infrastructure exists (`tests.py` files in apps)
- Django test framework
- No explicit test documentation found

### Admin Interface
- **URL:** `http://127.0.0.1:8000/<ADMIN_URL_PREFIX>/admin`
- **Default Credentials:** admin / adminpass
- **Features:** Full Django admin for all models

---

## Deployment Architecture

### Production Setup
- **Web Server:** Gunicorn
- **Reverse Proxy:** Assumed (nginx/Apache)
- **Static Files:** WhiteNoise (no separate web server needed)
- **Database:** PostgreSQL with connection pooling
- **Cache:** Redis recommended
- **Task Runner:** System crontab

### Optimization Features
- HTML minification (django-htmlmin)
- Brotli compression (django-brotli)
- Static file compression and caching
- Template caching (production only)
- Database query optimization

### Monitoring
- Sentry for error tracking
- Django admin for data inspection
- Redis board for cache inspection
- Custom logging

---

## Data Science Components

### Machine Learning
- **Libraries:** XGBoost, scikit-learn, datasieve
- **Purpose:** Likely for trend prediction and analysis
- **Data Processing:** NumPy, SciPy for numerical operations
- **Serialization:** cloudpickle for model persistence

### Statistical Analysis
- Linear regression for price trends
- Rarity score calculations
- Efficiency ratings
- Performance metrics

---

## Third-Party Integrations

### Included Libraries (in static/)
- jQuery UI 1.12.1
- Custom font libraries
- Image assets
- JSON payloads

### External Services
- Torn City API (primary data source)
- Discord integration (community)
- Sentry (error tracking)
- GitHub (development)

---

## Directory Structure

```
yata/
├── api/                 # API endpoints
├── awards/              # Achievement tracking
├── bazaar/              # Market tracking
├── company/             # Company management
├── cron/                # Scheduled tasks
├── faction/             # Faction management (largest app)
├── loot/                # NPC attack coordination
├── player/              # User accounts
├── setup/               # System setup
├── stock/               # Stock market (active)
├── stocks/              # Stock market (legacy)
├── target/              # Combat targets
├── templates/           # Django templates
├── yata/                # Core Django project
│   ├── settings.py      # Configuration
│   ├── urls.py          # URL routing
│   ├── static/          # Static assets
│   ├── media/           # Media files
│   └── src/             # Additional source code
├── manage.py            # Django management
├── requirements.txt     # Python dependencies
├── setup.py             # Initialization script
├── .pre-commit-config.yaml  # Code quality
└── README.md            # Setup documentation
```

---

## Code Quality Metrics

### Code Style
- **Line Length:** 200 characters
- **Formatting:** Black
- **Import Style:** isort with black profile
- **Linting:** flake8 with E203, W503, E501 ignored

### Best Practices
- Pre-commit hooks enforced
- Type hints (partial)
- Docstrings (variable)
- Comment density (moderate)

### Technical Debt
- Legacy `stocks` app not removed
- Some commented-out code
- Mixed line length standards
- Template caching only in production

---

## Community & Contribution

### Open Source
- **License:** GNU GPL v3
- **Contributing:** Via GitHub Flow
- **Issues:** Tracked via Discord
- **Pull Requests:** Encouraged with testing

### Community
- **Discord Server:** https://yata.yt/discord
- **Active Development:** Recent commits present
- **Documentation:** Basic setup guide in README

### Governance
- Maintainer approval for PRs
- Test suite must pass
- Code style enforced via pre-commit
- GPL v3 license agreement required

---

## Strengths

1. **Comprehensive Feature Set** - Covers all major Torn City activities
2. **Scalable Architecture** - Modular Django apps, optional Redis
3. **Code Quality** - Pre-commit hooks, formatters, linters
4. **Production Ready** - Compression, caching, monitoring
5. **Well-Organized** - Clear separation of concerns
6. **Active Cron System** - Real-time data updates
7. **API Integration** - Robust Torn City API usage
8. **Data Analytics** - ML/stats for trend analysis

---

## Areas for Improvement

1. **Testing Coverage** - Limited visible test infrastructure
2. **Documentation** - Could expand beyond basic setup
3. **Legacy Code** - `stocks` app should be removed
4. **CI/CD** - GitHub Actions workflow is backed up
5. **Type Hints** - Could expand Python typing
6. **Frontend** - Could modernize (React/Vue)
7. **API Documentation** - No visible API docs for external consumers

---

## Use Cases

### For Players
- Track market prices and trends
- Coordinate faction attacks
- Monitor NPC loot timings
- Analyze combat performance
- Track achievements and awards
- Manage company operations
- Investment analysis for stocks

### For Factions
- Member management
- Chain attack coordination
- War planning
- Performance tracking
- Data export for analysis
- Spy report integration

### For Developers
- RESTful API access
- Third-party integration
- Data export capabilities
- Client verification

---

## Conclusion

YATA is a mature, well-architected Django application serving as a comprehensive companion platform for Torn City. With ~42,000 lines of Python code across 11 Django apps, it provides deep integration with the game's API to offer analytics, tracking, and coordination tools.

The codebase demonstrates professional development practices with automated code quality checks, production-ready optimization features, and a modular architecture that allows for easy extension. The extensive cron job system ensures real-time data updates, while the optional Redis caching and PostgreSQL support make it scalable for production use.

Key strengths include its comprehensive feature coverage, code quality tooling, and active community support through Discord. Areas for improvement include expanding test coverage, modernizing the frontend stack, and completing CI/CD implementation.

The project is actively maintained under the GNU GPL v3 license and welcomes contributions from the community through a standard GitHub Flow process.

---

**Analysis prepared by:** GitHub Copilot Agent  
**Date:** February 18, 2026  
**Repository Version:** Current master branch
