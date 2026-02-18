# ✅ YATA Bazaar - Koyeb Deployment Checklist

## Pre-Deployment Checklist

### Repository Setup
- [x] Fork repository to your GitHub account
- [x] Clone forked repository locally (optional, for local testing)
- [x] Verify all files present:
  - [x] Procfile
  - [x] .env.example
  - [x] requirements.txt
  - [x] KOYEB_DEPLOYMENT.md
  - [x] README.md

### Koyeb Account Setup
- [ ] Create account at https://app.koyeb.com/
- [ ] Verify email address
- [ ] Connect GitHub account
- [ ] Optional: Add payment method (for paid plans)

## Deployment Steps

### 1. Create Koyeb App
- [ ] Click "Create App" in Koyeb dashboard
- [ ] Select "GitHub" as deployment method
- [ ] Choose your forked repository
- [ ] Select branch (usually `main` or `copilot/analyze-repo-structure`)
- [ ] Name your app (e.g., `yata-bazaar`)

### 2. Configure Build Settings
- [ ] Builder: Buildpack (auto-detected)
- [ ] Build command: Leave empty
- [ ] Run command: Leave empty (uses Procfile)

### 3. Set Environment Variables
- [ ] Click "Add Variable" for each:
  - [ ] `SECRET_KEY` = (generate 50-char random string)
    - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
    - Or use: https://djecrety.ir/
  - [ ] `DEBUG` = `False`
  - [ ] `ALLOWED_HOSTS` = `*` (or your domain)
  - [ ] `LOG_KEY` = (any string, e.g., `log-2026`)
  - [ ] `ADMIN_URL_PREFIX` = `admin/`

### 4. Add PostgreSQL Database
- [ ] Go to "Databases" tab
- [ ] Click "Create Database"
- [ ] Select "PostgreSQL"
- [ ] Choose plan (free tier available)
- [ ] Name: `yata-db` (or your choice)
- [ ] Click "Create"
- [ ] Wait for database to provision (~2 minutes)
- [ ] Verify `DATABASE_URL` added to environment variables automatically

### 5. Deploy Application
- [ ] Review all settings
- [ ] Click "Deploy"
- [ ] Wait 3-5 minutes for build and deployment
- [ ] Monitor build logs for errors
- [ ] Wait for status to show "Healthy"

### 6. Initial Setup (via Koyeb Console)
- [ ] Open app in Koyeb dashboard
- [ ] Click "Console" or "Shell" tab
- [ ] Run migration command:
  ```bash
  python manage.py migrate
  ```
- [ ] Collect static files:
  ```bash
  python manage.py collectstatic --noinput
  ```
- [ ] Create admin user:
  ```bash
  python manage.py createsuperuser
  ```
  - [ ] Enter username
  - [ ] Enter email
  - [ ] Enter password (twice)
- [ ] Populate item database:
  ```bash
  python manage.py items
  ```
  - Note: This requires a Torn API key (add via admin panel first)

### 7. Verify Deployment
- [ ] Visit app URL: `https://your-app-name.koyeb.app/`
- [ ] Check health endpoint: `https://your-app-name.koyeb.app/health/`
  - [ ] Should return: `{"status": "healthy", "database": "connected"}`
- [ ] Access admin panel: `https://your-app-name.koyeb.app/admin/`
  - [ ] Login with superuser credentials
  - [ ] Verify admin interface loads
- [ ] Test bazaar page: `https://your-app-name.koyeb.app/bazaar/`

## Post-Deployment Setup

### 8. Add Torn API Key
- [ ] Login to Torn City (https://www.torn.com/)
- [ ] Generate API key with appropriate permissions
- [ ] Go to admin panel: `/admin/setup/apikey/`
- [ ] Click "Add API Key"
- [ ] Paste your Torn API key
- [ ] Save

### 9. Populate Initial Data
- [ ] Run items command via console:
  ```bash
  python manage.py items
  ```
- [ ] Verify items appear in database
- [ ] Check bazaar page shows items

### 10. Configure Monitoring
- [ ] Enable Koyeb health monitoring (automatic)
- [ ] Optional: Set up alerts in Koyeb dashboard
- [ ] Optional: Configure Sentry for error tracking
  - [ ] Get Sentry DSN
  - [ ] Add environment variables:
    - `ENABLE_SENTRY` = `True`
    - `SENTRY_DSN` = (your DSN)
    - `SENTRY_ENVIRONMENT` = `production`
    - `SENTRY_SAMPLE_RATE` = `1.0`
  - [ ] Redeploy

## Optional Enhancements

### 11. Custom Domain (Optional)
- [ ] Go to app settings in Koyeb
- [ ] Click "Domains" tab
- [ ] Click "Add Domain"
- [ ] Enter your domain name
- [ ] Follow DNS configuration instructions
- [ ] Update `ALLOWED_HOSTS` to include your domain
- [ ] Redeploy

### 12. Scaling (Optional)
- [ ] Monitor app performance in dashboard
- [ ] If needed, upgrade instance size:
  - [ ] Small (1 GB) for moderate traffic
  - [ ] Medium (2 GB) for high traffic
- [ ] Or scale horizontally:
  - [ ] Increase number of instances
  - [ ] Koyeb auto-load-balances

### 13. Scheduled Tasks (Optional)
For automated item updates:
- [ ] Option A: Use external cron service
  - [ ] Sign up at cron-job.org
  - [ ] Create job to call API endpoint
  - [ ] Schedule: Daily or as needed
- [ ] Option B: Use Koyeb cron (if available)
  - [ ] Configure cron expression
  - [ ] Point to management command

## Troubleshooting Checklist

### If Deployment Fails
- [ ] Check build logs in Koyeb dashboard
- [ ] Verify all environment variables are set
- [ ] Ensure `DATABASE_URL` is present
- [ ] Check Python version compatibility (3.8+)
- [ ] Verify requirements.txt is correct

### If Health Check Fails
- [ ] Check application logs
- [ ] Verify database connection
- [ ] Run migrations if not done
- [ ] Check `DATABASE_URL` format
- [ ] Restart app in Koyeb

### If Static Files Don't Load
- [ ] Run `collectstatic` command
- [ ] Check `STATIC_ROOT` and `STATIC_URL` in settings
- [ ] Verify WhiteNoise is installed
- [ ] Check Koyeb logs for errors

### If Admin Panel Doesn't Work
- [ ] Verify superuser created successfully
- [ ] Check `ALLOWED_HOSTS` includes your domain
- [ ] Verify migrations applied
- [ ] Check session configuration

### If Items Don't Load
- [ ] Verify Torn API key added
- [ ] Check API key permissions
- [ ] Run `items` command manually
- [ ] Check application logs for errors
- [ ] Verify network connectivity to Torn API

## Maintenance Checklist

### Regular Maintenance
- [ ] Monitor app health in Koyeb dashboard
- [ ] Review logs for errors
- [ ] Check disk space usage
- [ ] Monitor database size
- [ ] Update dependencies when needed
- [ ] Run `items` command periodically (or set up cron)

### Security Maintenance
- [ ] Rotate `SECRET_KEY` periodically (requires restart)
- [ ] Update Django when security patches released
- [ ] Monitor Koyeb security advisories
- [ ] Review access logs for suspicious activity
- [ ] Keep API keys secure

### Performance Monitoring
- [ ] Check response times in Koyeb metrics
- [ ] Monitor CPU and memory usage
- [ ] Review database query performance
- [ ] Optimize slow queries if needed
- [ ] Scale up if resources constrained

## Success Criteria

Your deployment is successful when:
- [x] App URL loads without errors
- [x] Health endpoint returns 200 OK
- [x] Admin panel accessible and functional
- [x] Bazaar pages load with data
- [x] API endpoints respond correctly
- [x] Database queries work
- [x] Static files load properly
- [x] Logs show no critical errors

## Support Resources

If you need help:
- 📖 Read KOYEB_DEPLOYMENT.md for detailed instructions
- 📖 Check DEPLOYMENT_SUMMARY.md for quick reference
- 💬 Join YATA Discord: https://yata.yt/discord
- 🐛 Open GitHub issue for bugs
- 📧 Contact Koyeb support for platform issues

## Completion

Once all boxes are checked:
- ✅ Your YATA Bazaar is live and operational!
- ✅ Share your deployment with the community
- ✅ Start tracking market prices and trends
- ✅ Enjoy simplified Torn City market data!

---

**Last Updated:** 2026-02-18  
**Version:** 2.0.0 - Simplified Bazaar Version  
**Status:** Production Ready ✅
