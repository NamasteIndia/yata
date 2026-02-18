# Deploy YATA Bazaar to Koyeb

This guide will walk you through deploying the simplified YATA Bazaar application to Koyeb, a serverless platform that makes deployment easy.

## What's Included

This simplified version of YATA includes **only the Market/Bazaar features**:
- ✅ Item price tracking and history
- ✅ Market trend analysis (7-day and 31-day linear regression)
- ✅ Foreign stock tracking (crowdsourced from third-party tools)
- ✅ Real-time bazaar price updates
- ✅ API endpoints for external integrations

**Removed features:** Awards, Targets, Faction management, Company, Loot, Stocks

## Prerequisites

1. A [Koyeb account](https://app.koyeb.com/) (free tier available)
2. A [GitHub account](https://github.com/) to fork this repository
3. A [Torn City](https://www.torn.com/) API key (optional, for development)

## Quick Start Guide

### Step 1: Fork the Repository

1. Go to the [YATA repository](https://github.com/NamasteIndia/yata)
2. Click the **Fork** button in the top right
3. Wait for GitHub to create your fork

### Step 2: Create a Koyeb App

1. Log in to [Koyeb](https://app.koyeb.com/)
2. Click **Create App**
3. Select **GitHub** as the deployment method
4. Connect your GitHub account if not already connected
5. Select your forked YATA repository
6. Configure the following settings:

#### Build Settings
- **Builder**: Docker (Koyeb will auto-detect, or you can use Buildpack)
- **Branch**: `main` or your working branch
- **Build command**: Leave empty (Koyeb auto-detects)
- **Run command**: Leave empty (uses Procfile)

#### Instance Settings
- **Instance type**: `nano` (512 MB RAM, sufficient for small deployments)
- **Regions**: Choose your preferred region
- **Scaling**: Start with 1 instance (can scale up later)

#### Environment Variables

Click **Add Variable** and configure these required variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `SECRET_KEY` | (generate one) | Django secret key - use a random 50-char string |
| `DEBUG` | `False` | Must be False in production |
| `ALLOWED_HOSTS` | `*` | Or your specific Koyeb domain |
| `LOG_KEY` | `your-log-key` | Any string for logging |
| `ADMIN_URL_PREFIX` | `admin/` | URL prefix for Django admin |

**Database Configuration:**
Koyeb automatically provides a `DATABASE_URL` environment variable when you add a PostgreSQL database (see Step 3).

**Optional variables:**
- `ENABLE_SENTRY`: Set to `True` if using Sentry for error tracking
- `SENTRY_DSN`: Your Sentry DSN (if using Sentry)
- `SENTRY_ENVIRONMENT`: `production`

#### Generate a SECRET_KEY

Run this command locally to generate a secure secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use an online generator: https://djecrety.ir/

### Step 3: Add PostgreSQL Database

1. In your Koyeb app settings, go to the **Databases** tab
2. Click **Create Database**
3. Select **PostgreSQL**
4. Choose a plan (free tier available)
5. Name your database (e.g., `yata-db`)
6. Click **Create**

Koyeb will automatically:
- Create the database
- Add a `DATABASE_URL` environment variable to your app
- Connect your app to the database

### Step 4: Deploy

1. Review all settings
2. Click **Deploy**
3. Wait 3-5 minutes for the initial deployment

Koyeb will:
- Clone your repository
- Install dependencies from `requirements.txt`
- Set up the database connection
- Start the application using Gunicorn (defined in `Procfile`)

### Step 5: Run Database Migrations

After the first deployment, you need to initialize the database:

1. Go to your app in Koyeb dashboard
2. Click on **Console** or **Shell**
3. Run these commands:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

**For the superuser:**
- Username: `admin` (or your choice)
- Email: your email
- Password: create a strong password

### Step 6: Initialize Bazaar Data

To populate the item database, you need to run the setup command:

```bash
python manage.py items
```

This will:
- Fetch all items from Torn City API
- Create the item database
- Set up initial price tracking

**Note:** You need a valid Torn API key stored in the database for this to work. You can add one via the Django admin panel.

### Step 7: Access Your Application

Your app will be available at:
```
https://your-app-name.koyeb.app/
```

Access the admin panel at:
```
https://your-app-name.koyeb.app/admin/
```

## Health Check Endpoint

The application includes a health check endpoint at `/health/` that Koyeb uses to monitor your application:

```bash
curl https://your-app-name.koyeb.app/health/
```

Response when healthy:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Configuration Details

### Procfile

The `Procfile` defines how Koyeb runs your application:

```
web: gunicorn yata.wsgi --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60 --access-logfile - --error-logfile -
```

This configuration:
- Uses Gunicorn as the WSGI server
- Binds to the `$PORT` environment variable (provided by Koyeb)
- Runs 2 worker processes with 4 threads each
- 60-second timeout for requests
- Logs access and errors to stdout (visible in Koyeb logs)

### Database Connection

The application automatically detects and uses the `DATABASE_URL` environment variable:

```python
# Format: postgresql://user:password@host:port/dbname
DATABASE_URL=postgresql://user:pass@hostname:5432/yata
```

No manual database configuration needed!

### Static Files

Static files are served using WhiteNoise, which is configured in `settings.py`:

```python
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
```

This means:
- No separate static file server needed
- Files are compressed and cached
- Efficient serving in production

## Scaling and Performance

### Vertical Scaling (Instance Size)

For better performance, upgrade your instance:

1. **Nano (512 MB)**: Good for testing and light usage
2. **Small (1 GB)**: Recommended for production with moderate traffic
3. **Medium (2 GB)**: For higher traffic or complex queries

### Horizontal Scaling (Multiple Instances)

To handle more traffic:

1. Go to your app settings in Koyeb
2. Increase the number of instances (replicas)
3. Koyeb automatically load-balances between instances

### Database Scaling

For better database performance:

1. Upgrade your PostgreSQL plan
2. Enable connection pooling
3. Add read replicas for heavy read workloads

## Monitoring and Logs

### View Logs

1. Go to your app in Koyeb dashboard
2. Click the **Logs** tab
3. View real-time application logs

### Health Monitoring

Koyeb automatically monitors the `/health/` endpoint:
- Restarts unhealthy instances
- Shows health status in dashboard
- Alerts on failures (configure in settings)

### Metrics

Koyeb provides:
- CPU usage
- Memory usage
- Request count
- Response times
- Error rates

## Maintenance Tasks

### Update Application

When you push changes to GitHub:

1. Koyeb automatically detects the changes
2. Triggers a new build and deployment
3. Performs zero-downtime rolling update

### Run Management Commands

Use the Koyeb console to run Django commands:

```bash
# Update items from Torn API
python manage.py items

# Create database backup
python manage.py dumpdata > backup.json

# Clear cache
python manage.py clear_cache
```

### Database Migrations

After code changes that modify models:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### Application Won't Start

**Check logs** in Koyeb dashboard for errors:

Common issues:
- Missing environment variables
- Database connection errors
- Import errors from removed apps

**Solution:** Verify all required environment variables are set

### Database Connection Errors

**Error:** `could not connect to server`

**Solutions:**
1. Verify `DATABASE_URL` is set correctly
2. Ensure database is running (check Koyeb database status)
3. Check database credentials

### Static Files Not Loading

**Error:** 404 on CSS/JS files

**Solutions:**
1. Run `python manage.py collectstatic` in Koyeb console
2. Verify `STATIC_ROOT` and `STATIC_URL` in settings
3. Check WhiteNoise is installed: `pip show whitenoise`

### Health Check Failing

**Error:** Health endpoint returns 503

**Solutions:**
1. Check database connection
2. Review application logs
3. Verify all migrations are applied

### Out of Memory Errors

**Error:** Application crashes with memory errors

**Solutions:**
1. Upgrade to larger instance (Small or Medium)
2. Optimize database queries
3. Reduce worker/thread count in Procfile

### Import Errors After Deployment

**Error:** `ModuleNotFoundError: No module named 'faction'`

**Cause:** Code still references removed apps

**Solution:** 
1. Check `settings.py` INSTALLED_APPS
2. Check URL imports in `urls.py`
3. Check template references
4. Remove import statements for removed apps

## Security Best Practices

### 1. Secret Key
- Use a strong, random SECRET_KEY
- Never commit it to version control
- Rotate periodically

### 2. Debug Mode
- Always set `DEBUG=False` in production
- Use Sentry for error tracking instead

### 3. Allowed Hosts
- Set specific domains instead of `*`
- Example: `ALLOWED_HOSTS=your-app.koyeb.app`

### 4. HTTPS
- Koyeb provides automatic HTTPS
- Enforce HTTPS in Django settings (already configured)

### 5. Database Security
- Use strong database passwords
- Enable SSL for database connections
- Regular backups

### 6. API Keys
- Store Torn API keys in database, not environment variables
- Use API key rotation
- Limit key permissions

## Cost Optimization

### Free Tier Limits

Koyeb free tier includes:
- 1 nano instance
- Shared CPU
- 100 GB bandwidth/month

**Tips:**
- Use database caching to reduce queries
- Optimize images and static files
- Monitor bandwidth usage

### Paid Plans

For production:
- **Hobby ($5/month)**: Better performance, more bandwidth
- **Pro ($20/month)**: Multiple instances, autoscaling
- **Enterprise**: Custom pricing, dedicated resources

## Advanced Configuration

### Custom Domain

1. Go to Koyeb app settings
2. Click **Domains**
3. Click **Add Domain**
4. Follow DNS configuration instructions

### Environment-Specific Settings

Use multiple environment variables for different environments:

```bash
# Development
DEBUG=True
SENTRY_ENVIRONMENT=development

# Staging
DEBUG=False
SENTRY_ENVIRONMENT=staging

# Production
DEBUG=False
SENTRY_ENVIRONMENT=production
```

### Scheduled Tasks (Cron)

For periodic tasks (like updating items):

**Option 1:** Use Koyeb's built-in cron (if available)

**Option 2:** Use external service:
- [Cron-job.org](https://cron-job.org)
- Call your API endpoint: `https://your-app.koyeb.app/api/v1/travel/import/`

**Option 3:** Use Django-cron or Celery
- Add to requirements.txt
- Configure in settings.py
- Add worker Procfile entry

## API Usage

### Foreign Stock Import

Third-party tools can submit stock data:

```bash
curl -X POST https://your-app.koyeb.app/api/v1/travel/import/ \
  -H "Content-Type: application/json" \
  -d '{
    "country": "jap",
    "items": [
      {"id": 197, "quantity": 152, "cost": 25000}
    ],
    "client": "MyTool",
    "version": "1.0"
  }'
```

### Foreign Stock Export

Retrieve aggregated stock data:

```bash
curl https://your-app.koyeb.app/api/v1/travel/export/
```

## Support and Resources

### Official Resources
- [Koyeb Documentation](https://www.koyeb.com/docs)
- [Django Documentation](https://docs.djangoproject.com/)
- [YATA Discord](https://yata.yt/discord)

### Community
- GitHub Issues: Report bugs or request features
- Discord: Get help from the community

### Need Help?
- Check Koyeb logs first
- Review this guide
- Ask in YATA Discord
- Open a GitHub issue

## Migration from Other Hosts

### From Heroku

1. Export your database: `heroku pg:backups:capture`
2. Download backup: `heroku pg:backups:download`
3. Import to Koyeb PostgreSQL
4. Update environment variables
5. Deploy to Koyeb

### From Local Development

1. Fork repository to GitHub
2. Push your changes
3. Follow deployment steps above
4. Migrate database data using Django fixtures

## Conclusion

You now have a fully functional YATA Bazaar deployment on Koyeb! The application will:
- Track item prices and trends
- Accept foreign stock data from third-party tools
- Provide API endpoints for integrations
- Scale automatically as needed

**Next steps:**
1. Configure your Torn API keys in admin panel
2. Run the `items` command to populate the database
3. Set up monitoring and alerts
4. Share your deployment with the community!

For questions or issues, visit the [YATA Discord](https://yata.yt/discord) or open a GitHub issue.

Happy trading! 🎯
