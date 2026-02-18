# YATA Bazaar - Market Data Tracker

[![Commit activity](https://img.shields.io/github/commit-activity/m/NamasteIndia/yata?color=%23447e9b&logo=github&logoColor=white&style=for-the-badge)](https://github.com/NamasteIndia/yata/commits)
[![Last commit](https://img.shields.io/github/last-commit/NamasteIndia/yata?color=%23447e9b&logo=github&logoColor=white&style=for-the-badge)](https://github.com/NamasteIndia/yata/commits/main)

## Simplified Version - Market/Bazaar Data Only

This is a **simplified version** of YATA (Yet Another Torn App) focused exclusively on **Market/Bazaar data tracking** for [Torn City](https://www.torn.com/).

### Features Included ✅

- **Item Price Tracking**: Monitor current bazaar prices and market values
- **Price History**: 31-day price history with hourly granularity
- **Trend Analysis**: 7-day and 31-day price trends using linear regression
- **Foreign Stocks**: Crowdsourced foreign stock data from third-party tools
- **Real-Time Updates**: User-initiated bazaar price refreshes
- **API Endpoints**: External integrations for stock import/export

### Features Removed ❌

This version has removed:
- Awards tracking
- Target management
- Faction tools
- Company management
- Loot timers
- Stock market tracking

For the full-featured version, see the [original YATA repository](https://github.com/Kivou-2000607/yata).

## Quick Deploy to Koyeb

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/)

See [KOYEB_DEPLOYMENT.md](KOYEB_DEPLOYMENT.md) for detailed deployment instructions.

## Local Development Setup

### Prerequisites

- Python 3.8+
- pip
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NamasteIndia/yata.git
   cd yata
   ```

2. **Install dependencies**
   ```bash
   pip install -U pip
   pip install -r requirements.txt
   ```

3. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set required variables:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=*
   LOG_KEY=your-log-key
   DATABASE=sqlite
   ```

4. **Initialize database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Web interface: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

### Populate Bazaar Data

To fetch items from Torn City API:

```bash
python manage.py items
```

**Note:** You need a Torn API key. Add it via the Django admin panel at `/admin/setup/apikey/`.

## Production Deployment

### Environment Variables

Required for production:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Random 50-char string |
| `DEBUG` | Debug mode (False in prod) | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `your-domain.com` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `LOG_KEY` | Logging key | Any string |

Optional:

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_SENTRY` | Enable Sentry error tracking | `False` |
| `SENTRY_DSN` | Sentry DSN | - |
| `CACHE_RESPONSE` | Cache duration (seconds) | `10` |

### Deploy to Koyeb

See [KOYEB_DEPLOYMENT.md](KOYEB_DEPLOYMENT.md) for step-by-step instructions.

### Deploy to Other Platforms

The application works on any platform that supports:
- Python 3.8+
- PostgreSQL
- WSGI servers (Gunicorn)

The `Procfile` is configured for Heroku-compatible platforms:
```
web: gunicorn yata.wsgi --bind 0.0.0.0:$PORT --workers 2 --threads 4
```

## API Documentation

### Health Check

```bash
GET /health/
```

Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Foreign Stock Import

Submit stock data from foreign countries:

```bash
POST /api/v1/travel/import/
Content-Type: application/json

{
  "country": "jap",
  "items": [
    {"id": 197, "quantity": 152, "cost": 25000},
    {"id": 198, "quantity": 89, "cost": 12000}
  ],
  "client": "YourToolName",
  "version": "1.0.0"
}
```

**Countries:** mex, cay, can, haw, uni, arg, swi, jap, chi, uae, sou

### Foreign Stock Export

Retrieve aggregated stock data:

```bash
GET /api/v1/travel/export/
```

Response:
```json
{
  "stocks": {
    "jap": {
      "update": 1708245600,
      "stocks": [
        {
          "id": 197,
          "name": "Erotic DVD",
          "quantity": 152,
          "cost": 25000
        }
      ]
    }
  },
  "timestamp": 1708245723
}
```

## Architecture

### Technology Stack

- **Backend**: Django 4.2.25
- **Database**: PostgreSQL (or SQLite for development)
- **Server**: Gunicorn
- **Static Files**: WhiteNoise
- **Caching**: Django database cache
- **Analytics**: NumPy, SciPy (linear regression)

### Data Models

- **Item**: Item details, price history, trend analysis
- **MarketData**: Current bazaar listings (price points)
- **AbroadStocks**: Foreign country stock data
- **BazaarData**: Global configuration and statistics

### Price Trend Analysis

The application uses **linear regression** (scipy) to calculate price trends:

- **7-day trend**: Short-term price movement
- **31-day trend**: Long-term price movement

Trends are stored as:
- Slope (A): Price change per second
- Intercept (B): Y-intercept
- Normalized tendency: Percentage change

## Project Structure

```
yata/
├── api/                    # API endpoints
│   └── views/
│       ├── main.py        # Root API
│       └── travel.py      # Foreign stocks
├── bazaar/                # Bazaar app (main feature)
│   ├── models.py         # Item, MarketData, AbroadStocks
│   ├── views.py          # Web interface
│   ├── urls.py           # URL routing
│   └── management/
│       └── commands/
│           └── items.py  # Item sync command
├── player/               # Minimal user management
├── setup/                # Configuration
├── yata/                 # Django project
│   ├── settings.py      # Configuration
│   ├── urls.py          # URL routing
│   └── views.py         # Health check
├── templates/           # HTML templates
├── Procfile            # Koyeb/Heroku deployment
├── requirements.txt    # Python dependencies
└── manage.py          # Django management
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (if available)
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GNU General Public License v3.0 - see [LICENSE.md](LICENSE.md) for details.

## Credits

- Original YATA by [Kivou](https://github.com/Kivou-2000607)
- Simplified for Koyeb deployment
- [Torn City](https://www.torn.com/) for the game and API

## Support

- **Documentation**: [KOYEB_DEPLOYMENT.md](KOYEB_DEPLOYMENT.md), [BAZAAR_DATA_COLLECTION.md](BAZAAR_DATA_COLLECTION.md)
- **Discord**: [YATA Discord](https://yata.yt/discord)
- **Issues**: [GitHub Issues](https://github.com/NamasteIndia/yata/issues)

## Changelog

### v2.0.0 - Simplified Bazaar Version
- ✅ Removed non-bazaar features (awards, targets, faction, etc.)
- ✅ Simplified dependencies (removed ML libraries, Redis, etc.)
- ✅ Added Koyeb deployment support
- ✅ Added health check endpoint
- ✅ Improved database configuration (DATABASE_URL support)
- ✅ Updated documentation

### v1.x - Full Featured Version
- See [original repository](https://github.com/Kivou-2000607/yata) for history

## Roadmap

Potential future improvements:

- [ ] Automated item sync (scheduled tasks)
- [ ] Price alerts and notifications
- [ ] Mobile-responsive UI improvements
- [ ] GraphQL API
- [ ] WebSocket support for real-time updates
- [ ] Advanced filtering and search
- [ ] Data export features (CSV, JSON)

## FAQ

**Q: Why is this simplified?**  
A: To make deployment easier and reduce complexity. Focus on core bazaar functionality.

**Q: Can I add back removed features?**  
A: Yes! Check the original YATA repository and merge the features you need.

**Q: How often does data update?**  
A: Item metadata updates when you run the `items` command. Bazaar prices update on-demand when users click "Update".

**Q: Is this free to host?**  
A: Yes! Koyeb offers a free tier that's sufficient for personal use.

**Q: Can I use this commercially?**  
A: Check the GPL-3.0 license. Generally yes, but you must open-source your modifications.

---

Made with ❤️ for the Torn City community
