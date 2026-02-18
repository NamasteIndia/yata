# YATA Bazaar - Deployment Summary

## What Was Done

This repository has been simplified to focus exclusively on **Market/Bazaar data tracking** and made ready for deployment on **Koyeb**.

## Changes Made

### 1. **Removed Features**
The following Django apps and features were removed from INSTALLED_APPS:
- ❌ awards (Achievement tracking)
- ❌ target (Combat target management)
- ❌ faction (Faction/guild tools)
- ❌ stocks (Stock market tracking)
- ❌ company (Company management)
- ❌ loot (NPC loot timers)

### 2. **Kept Features**
- ✅ **bazaar** - Item price tracking, trends, foreign stocks
- ✅ **player** - Minimal user authentication (simplified)
- ✅ **setup** - Configuration management
- ✅ **api** - Travel endpoints for foreign stock import/export

### 3. **Added Deployment Support**

#### Files Created:
- **Procfile** - Koyeb/Heroku deployment configuration with Gunicorn
- **.env.example** - Environment variable template
- **KOYEB_DEPLOYMENT.md** - Comprehensive deployment guide (12KB)
- **README.md** - Updated documentation (8.6KB)
- **Health Check** - `/health/` endpoint for monitoring

#### Files Modified:
- **requirements.txt** - Simplified dependencies (removed Redis, ML libraries, etc.)
- **yata/settings.py** - DATABASE_URL support, removed unused apps, optional nplusone
- **yata/urls.py** - Removed non-bazaar routes, added health check
- **yata/views.py** - Added health check endpoint
- **yata/context_processors.py** - Removed loot-related processors
- **api/urls.py** - Keep only travel endpoints
- **player/admin.py** - Removed faction/other model registrations
- **player/functions.py** - Removed faction/awards/company dependencies

## Current State

### ✅ Verified Working:
1. Django check passes with no errors
2. Database migrations apply successfully
3. Health endpoint returns 200 OK with JSON: `{"status": "healthy", "database": "connected"}`
4. Development server starts without errors
5. All core imports resolve correctly

### Configuration:
- **Database**: Supports both SQLite (dev) and PostgreSQL (production via DATABASE_URL)
- **Static Files**: WhiteNoise for efficient serving
- **WSGI Server**: Gunicorn (configured in Procfile)
- **Caching**: Django database cache (simple, no Redis needed)
- **Dependencies**: Minimal - Django, NumPy, SciPy, Gunicorn, psycopg2-binary

## How to Deploy to Koyeb

See **[KOYEB_DEPLOYMENT.md](KOYEB_DEPLOYMENT.md)** for the complete step-by-step guide.

### Quick Start:

1. **Fork this repository** on GitHub

2. **Create Koyeb app**:
   - Connect your GitHub account
   - Select the forked repository
   - Choose branch

3. **Set environment variables**:
   ```
   SECRET_KEY=<generate-random-50-char-string>
   DEBUG=False
   ALLOWED_HOSTS=*
   LOG_KEY=your-log-key
   ```

4. **Add PostgreSQL database**:
   - Koyeb auto-provides `DATABASE_URL`
   - No manual configuration needed

5. **Deploy and wait 3-5 minutes**

6. **Run initial setup** (via Koyeb console):
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   python manage.py items  # Populate item database
   ```

7. **Access your app**:
   - Web: `https://your-app-name.koyeb.app/`
   - Admin: `https://your-app-name.koyeb.app/admin/`
   - Health: `https://your-app-name.koyeb.app/health/`

## API Endpoints

### Health Check
```bash
GET /health/
# Returns: {"status": "healthy", "database": "connected"}
```

### Foreign Stock Import
```bash
POST /api/v1/travel/import/
Content-Type: application/json

{
  "country": "jap",
  "items": [{"id": 197, "quantity": 152, "cost": 25000}],
  "client": "MyTool",
  "version": "1.0"
}
```

### Foreign Stock Export
```bash
GET /api/v1/travel/export/
# Returns aggregated stock data from all countries
```

## Technology Stack

- **Backend**: Django 4.2.25
- **Python**: 3.8+
- **Database**: PostgreSQL (production) / SQLite (development)
- **Server**: Gunicorn
- **Static Files**: WhiteNoise
- **Math**: NumPy, SciPy (for linear regression trends)

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your values

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run server
python manage.py runserver

# Test health check
curl http://127.0.0.1:8000/health/
```

## Files Structure

```
yata/
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore patterns
├── Procfile              # Koyeb/Heroku deployment config
├── requirements.txt      # Python dependencies (simplified)
├── manage.py             # Django management script
├── README.md             # This file (simplified version)
├── README_ORIGINAL.md    # Original full-featured README
├── KOYEB_DEPLOYMENT.md   # Deployment guide
├── BAZAAR_DATA_COLLECTION.md  # How data is collected
├── REPOSITORY_ANALYSIS.md     # Technical analysis
│
├── api/                  # API endpoints
│   ├── urls.py          # API routing (travel only)
│   └── views/
│       ├── main.py      # Root endpoint
│       └── travel.py    # Foreign stock endpoints
│
├── bazaar/              # Main feature
│   ├── models.py        # Item, MarketData, AbroadStocks
│   ├── views.py         # Web interface
│   ├── urls.py          # Bazaar routing
│   └── management/
│       └── commands/
│           └── items.py # Item sync command
│
├── player/              # Simplified user management
│   ├── models.py        # Player, Key, Message
│   ├── admin.py         # Admin interface (simplified)
│   └── functions.py     # Helper functions (simplified)
│
├── setup/               # Configuration
│   └── models.py        # APIKey, Settings
│
└── yata/                # Django project
    ├── settings.py      # Configuration (DATABASE_URL support)
    ├── urls.py          # Main routing (health check added)
    ├── views.py         # Health check endpoint
    └── context_processors.py  # Template context (simplified)
```

## Migration from Full Version

If you're migrating from the full-featured YATA:

1. **Backup your database** - The removed apps' data won't be accessible
2. **Export important data** - Use Django's dumpdata before switching
3. **Note**: Player accounts and bazaar data will be preserved
4. **Warning**: Faction, awards, targets, company, loot data won't be accessible

## Monitoring

### Health Check
Koyeb automatically monitors `/health/` endpoint:
- Returns 200 OK when healthy
- Returns 503 when database connection fails
- Visible in Koyeb dashboard

### Logs
View real-time logs in Koyeb dashboard:
- Application logs
- Database queries
- Error messages
- Access logs

### Metrics
Koyeb provides:
- CPU usage
- Memory usage
- Request rate
- Response times
- Error rates

## Troubleshooting

### Issue: Health check fails
**Solution**: Check database connection and migrations
```bash
python manage.py migrate
python manage.py check
```

### Issue: Static files not loading
**Solution**: Run collectstatic
```bash
python manage.py collectstatic --noinput
```

### Issue: Import errors
**Solution**: Verify all dependencies installed
```bash
pip install -r requirements.txt
```

### Issue: Database connection errors
**Solution**: Verify DATABASE_URL environment variable
```bash
echo $DATABASE_URL
```

## Performance Tips

1. **Use connection pooling** - Included in settings (CONN_MAX_AGE=600)
2. **Enable caching** - Database cache is active
3. **Optimize queries** - N+1 detection available in DEBUG mode
4. **Scale instances** - Use Koyeb's scaling features
5. **Monitor metrics** - Watch memory/CPU usage in dashboard

## Security

- ✅ DEBUG=False in production
- ✅ Strong SECRET_KEY required
- ✅ HTTPS enforced (Koyeb auto-provides)
- ✅ ALLOWED_HOSTS configured
- ✅ CSRF protection enabled
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection (Django templates)

## Support

- **Documentation**: See [KOYEB_DEPLOYMENT.md](KOYEB_DEPLOYMENT.md)
- **Issues**: GitHub Issues tab
- **Discord**: [YATA Discord](https://yata.yt/discord)

## License

GNU General Public License v3.0 - see [LICENSE.md](LICENSE.md)

## Credits

- Original YATA by [Kivou](https://github.com/Kivou-2000607)
- Simplified and optimized for Koyeb deployment
- [Torn City](https://www.torn.com/) for the game and API

## What's Next?

After deployment, consider:

1. **Set up scheduled tasks** - Use external cron service to call `/api/v1/travel/import/`
2. **Configure custom domain** - Add your domain in Koyeb
3. **Enable Sentry** - For error tracking and monitoring
4. **Scale up** - Upgrade instance size if needed
5. **Add features** - Customize for your needs

---

**Status**: ✅ Ready for Koyeb deployment  
**Last Updated**: 2026-02-18  
**Version**: 2.0.0 (Simplified Bazaar Version)
