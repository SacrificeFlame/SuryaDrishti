# DNS Troubleshooting Guide - suryadrishti.in

This guide helps you diagnose and fix DNS issues for your custom domain.

## Quick DNS Check Commands

### 1. Check if DNS is resolving

**Windows (PowerShell):**
```powershell
nslookup www.suryadrishti.in
nslookup suryadrishti.in
```

**Linux/Mac:**
```bash
dig www.suryadrishti.in
dig suryadrishti.in
```

**Online Tools:**
- https://dnschecker.org/#A/www.suryadrishti.in
- https://www.whatsmydns.net/#A/www.suryadrishti.in
- https://mxtoolbox.com/DNSLookup.aspx

### 2. Check Railway Domain Configuration

1. Go to Railway Dashboard
2. Navigate to your frontend service
3. Go to **Settings** → **Networking** → **Public Networking**
4. Check if `www.suryadrishti.in` shows:
   - ✅ Green checkmark (Setup complete)
   - Domain status
   - Railway-provided target domain

## Common DNS Issues

### Issue 1: DNS Records Not Configured

**Problem:** DNS records are missing or incorrect in your DNS provider.

**Solution:**
1. Get the Railway target domain from Railway dashboard
2. Go to your DNS provider (Cloudflare, Namecheap, GoDaddy, etc.)
3. Add CNAME record:
   ```
   Type: CNAME
   Name: www
   Value: [Railway-provided-domain].railway.app
   TTL: 3600 (or Auto)
   ```

### Issue 2: DNS Propagation Delay

**Problem:** DNS changes can take 24-48 hours to propagate globally.

**Solution:**
- Wait for propagation (usually 1-4 hours, max 48 hours)
- Check DNS propagation status using online tools
- Clear your local DNS cache

### Issue 3: Incorrect CNAME Target

**Problem:** CNAME points to wrong Railway domain.

**Solution:**
1. Verify Railway domain in Railway dashboard
2. Update CNAME record to match exactly
3. Remove any trailing dots or extra characters

### Issue 4: Root Domain (suryadrishti.in) Not Working

**Problem:** Only `www.suryadrishti.in` works, not `suryadrishti.in`.

**Solution:**
- Option A: Add A record for root domain (if Railway provides IP)
- Option B: Add CNAME for root domain pointing to www
- Option C: Use DNS provider's redirect feature (www → root or root → www)

### Issue 5: DNS Cache Issues

**Problem:** Your computer/browser has cached old DNS records.

**Solution:**

**Windows:**
```powershell
# Flush DNS cache
ipconfig /flushdns

# Clear browser cache
# Chrome: Ctrl+Shift+Delete
# Firefox: Ctrl+Shift+Delete
```

**Mac/Linux:**
```bash
# Flush DNS cache (macOS)
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

# Linux (systemd-resolved)
sudo systemd-resolve --flush-caches
```

**Browser:**
- Clear browser cache
- Use incognito/private mode
- Try different browser

## Step-by-Step DNS Setup

### Step 1: Get Railway Domain

1. Go to Railway Dashboard
2. Select your frontend service
3. Go to **Settings** → **Networking**
4. Find your Railway domain (e.g., `suryadrishti-front-production.up.railway.app`)
5. Copy this domain

### Step 2: Configure DNS Records

**For www.suryadrishti.in (Recommended):**

1. Login to your DNS provider
2. Find DNS management / DNS settings
3. Add CNAME record:
   ```
   Type: CNAME
   Host/Name: www
   Value/Points to: suryadrishti-front-production.up.railway.app
   TTL: 3600 (1 hour) or Auto
   ```
4. Save changes

**For root domain suryadrishti.in (Optional):**

**Option A: CNAME (if your DNS provider supports it)**
```
Type: CNAME
Host/Name: @
Value/Points to: www.suryadrishti.in
TTL: 3600
```

**Option B: A Record (if Railway provides IP)**
```
Type: A
Host/Name: @
Value/Points to: [Railway IP Address]
TTL: 3600
```

**Option C: Redirect (DNS Provider Feature)**
- Use your DNS provider's redirect feature
- Redirect `suryadrishti.in` → `www.suryadrishti.in`

### Step 3: Verify DNS Configuration

Wait 5-10 minutes, then check:

```powershell
# Check CNAME record
nslookup -type=CNAME www.suryadrishti.in

# Check A record (if configured)
nslookup -type=A www.suryadrishti.in
```

Expected output should show:
- CNAME pointing to Railway domain
- Or A record pointing to Railway IP

### Step 4: Check Railway Domain Status

1. Go to Railway Dashboard
2. Check if domain shows "Setup complete" ✅
3. Check SSL certificate status (should be "Active" or "Provisioning")
4. Check domain logs for any errors

### Step 5: Test Website

1. Wait for DNS propagation (1-4 hours)
2. Visit `https://www.suryadrishti.in`
3. Check browser console for errors
4. Verify SSL certificate is valid (padlock icon)

## DNS Provider-Specific Instructions

### Cloudflare

1. Login to Cloudflare
2. Select your domain `suryadrishti.in`
3. Go to **DNS** → **Records**
4. Add CNAME:
   - Type: CNAME
   - Name: www
   - Target: `[railway-domain].railway.app`
   - Proxy status: DNS only (grey cloud) or Proxied (orange cloud)
   - TTL: Auto
5. Save

**Note:** If using Cloudflare proxy (orange cloud), Railway SSL might not work. Use "DNS only" mode.

### Namecheap

1. Login to Namecheap
2. Go to **Domain List** → Select `suryadrishti.in`
3. Click **Manage** → **Advanced DNS**
4. Add CNAME:
   - Type: CNAME Record
   - Host: www
   - Value: `[railway-domain].railway.app`
   - TTL: Automatic
5. Save

### GoDaddy

1. Login to GoDaddy
2. Go to **My Products** → **DNS**
3. Add CNAME:
   - Type: CNAME
   - Name: www
   - Value: `[railway-domain].railway.app`
   - TTL: 600 (10 minutes)
4. Save

### Google Domains

1. Login to Google Domains
2. Select `suryadrishti.in`
3. Go to **DNS** → **Custom records**
4. Add CNAME:
   - Name: www
   - Type: CNAME
   - Data: `[railway-domain].railway.app`
   - TTL: 3600
5. Save

## Troubleshooting Commands

### Check DNS Records

```powershell
# Windows PowerShell
Resolve-DnsName www.suryadrishti.in
Resolve-DnsName suryadrishti.in

# Check specific record types
nslookup -type=CNAME www.suryadrishti.in
nslookup -type=A www.suryadrishti.in
nslookup -type=MX suryadrishti.in
```

### Check DNS Propagation

```bash
# Using dig (Linux/Mac)
dig @8.8.8.8 www.suryadrishti.in
dig @1.1.1.1 www.suryadrishti.in

# Check from multiple DNS servers
dig @8.8.8.8 www.suryadrishti.in +short
dig @1.1.1.1 www.suryadrishti.in +short
dig @208.67.222.222 www.suryadrishti.in +short
```

### Test HTTP/HTTPS Connection

```powershell
# Test HTTP connection
curl -I http://www.suryadrishti.in

# Test HTTPS connection
curl -I https://www.suryadrishti.in

# Test with verbose output
curl -v https://www.suryadrishti.in
```

## Common Error Messages

### "This site can't be reached"

**Causes:**
- DNS not resolving
- DNS records not configured
- DNS propagation not complete

**Solution:**
- Check DNS records are correct
- Wait for DNS propagation
- Clear DNS cache

### "SSL Certificate Error"

**Causes:**
- SSL certificate not provisioned
- DNS not fully propagated
- Wrong domain configuration

**Solution:**
- Wait for Railway to provision SSL (5-30 minutes)
- Verify DNS is resolving correctly
- Check Railway domain status

### "Connection Timeout"

**Causes:**
- Railway service not running
- Wrong port configuration
- Firewall blocking connection

**Solution:**
- Check Railway service status
- Verify service is deployed
- Check Railway logs

## Railway-Specific Checks

### 1. Verify Domain in Railway

1. Go to Railway Dashboard
2. Select frontend service
3. **Settings** → **Networking** → **Public Networking**
4. Verify:
   - Domain: `www.suryadrishti.in`
   - Status: Setup complete ✅
   - SSL: Active/Provisioning
   - Target: Railway service domain

### 2. Check Railway Logs

1. Go to Railway Dashboard
2. Select frontend service
3. Go to **Deployments** → **Logs**
4. Look for:
   - Domain configuration errors
   - SSL certificate errors
   - DNS validation errors

### 3. Verify Railway Service is Running

1. Check service status in Railway
2. Verify latest deployment is successful
3. Check if service is responding on Railway domain
4. Test: `https://[railway-domain].railway.app`

## Quick Fix Checklist

- [ ] DNS CNAME record added in DNS provider
- [ ] CNAME points to correct Railway domain
- [ ] DNS TTL set to reasonable value (3600 or Auto)
- [ ] Waited at least 5-10 minutes after DNS change
- [ ] Cleared local DNS cache
- [ ] Verified Railway domain status is "Setup complete"
- [ ] Checked Railway service is running
- [ ] Tested Railway domain directly (should work)
- [ ] Verified SSL certificate is active
- [ ] Checked browser console for errors
- [ ] Tested in incognito/private mode

## Still Not Working?

1. **Double-check DNS records:**
   - Verify CNAME is exactly correct
   - Check for typos
   - Verify TTL is set

2. **Check Railway configuration:**
   - Verify domain is added in Railway
   - Check domain status
   - Verify SSL certificate

3. **Wait longer:**
   - DNS can take up to 48 hours
   - Usually works within 1-4 hours
   - Check propagation status online

4. **Contact support:**
   - Railway support: https://railway.app/help
   - DNS provider support
   - Check Railway status page

## Testing Your Setup

Once DNS is working, test:

1. **HTTP Test:**
   ```powershell
   curl http://www.suryadrishti.in
   ```

2. **HTTPS Test:**
   ```powershell
   curl https://www.suryadrishti.in
   ```

3. **Browser Test:**
   - Visit `https://www.suryadrishti.in`
   - Check SSL certificate (padlock icon)
   - Test website functionality

4. **API Test:**
   - Check if frontend can connect to backend
   - Verify CORS is working
   - Test API endpoints

## Expected Timeline

- **DNS Propagation:** 1-4 hours (can take up to 48 hours)
- **SSL Certificate:** 5-30 minutes after DNS resolves
- **Full Setup:** Usually working within 2-4 hours

## Need Help?

If DNS is still not working after 24 hours:
1. Verify DNS records are correct
2. Check Railway domain configuration
3. Contact Railway support
4. Contact DNS provider support

