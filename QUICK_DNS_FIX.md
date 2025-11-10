# Quick DNS Fix for suryadrishti.in

## Immediate Steps

### 1. Check Current DNS Status

Run these commands to see what's configured:

```powershell
# Check www subdomain
nslookup www.suryadrishti.in

# Check root domain
nslookup suryadrishti.in

# Check CNAME record specifically
nslookup -type=CNAME www.suryadrishti.in
```

### 2. Get Railway Domain

1. Go to Railway Dashboard
2. Select your **frontend** service
3. Go to **Settings** → **Networking** → **Public Networking**
4. Find the domain that shows "Setup complete" ✅
5. Copy the Railway domain (e.g., `suryadrishti-front-production.up.railway.app`)

### 3. Configure DNS in Your DNS Provider

**You need to add a CNAME record:**

```
Type: CNAME
Name: www
Value: [Your Railway Domain].railway.app
TTL: 3600 (or Auto)
```

### 4. Common Issues and Fixes

#### Issue: DNS Not Propagating

**Fix:**
- Wait 1-4 hours (can take up to 48 hours)
- Clear DNS cache: `ipconfig /flushdns`
- Check propagation: https://dnschecker.org/#CNAME/www.suryadrishti.in

#### Issue: Wrong CNAME Target

**Fix:**
- Verify Railway domain is correct
- Update CNAME to match exactly
- Remove any trailing dots

#### Issue: Root Domain Not Working

**Fix:**
- Add CNAME for root domain: `@` → `www.suryadrishti.in`
- Or add A record if Railway provides IP
- Or use DNS provider's redirect feature

### 5. Verify Setup

After configuring DNS:

1. **Wait 10-15 minutes**
2. **Check DNS:**
   ```powershell
   nslookup www.suryadrishti.in
   ```
   Should show Railway domain

3. **Test Website:**
   - Visit `https://www.suryadrishti.in`
   - Should load your Railway app

4. **Check SSL:**
   - Should see padlock icon
   - Certificate should be valid

## Railway Domain Configuration

Make sure in Railway:

1. **Domain is added:**
   - Go to frontend service → Settings → Networking
   - Domain `www.suryadrishti.in` should be listed
   - Status should be "Setup complete" ✅

2. **SSL is active:**
   - SSL certificate should be "Active" or "Provisioning"
   - Wait 5-30 minutes for SSL to provision

3. **Service is running:**
   - Check that frontend service is deployed
   - Verify latest deployment is successful

## DNS Provider Instructions

### If using Cloudflare:
1. Login → Select domain → DNS → Records
2. Add CNAME: `www` → `[railway-domain].railway.app`
3. **Important:** Use "DNS only" (grey cloud), not "Proxied" (orange cloud)

### If using Namecheap:
1. Domain List → Manage → Advanced DNS
2. Add CNAME: Host `www`, Value `[railway-domain].railway.app`

### If using GoDaddy:
1. My Products → DNS
2. Add CNAME: Name `www`, Value `[railway-domain].railway.app`

## Still Not Working?

1. **Verify DNS records are correct** (check for typos)
2. **Wait longer** (DNS can take 24-48 hours)
3. **Clear DNS cache** on your computer
4. **Check Railway logs** for domain errors
5. **Test Railway domain directly** (should work if service is running)

## Quick Test

Test if Railway service is working:
```powershell
# Replace with your actual Railway domain
curl https://suryadrishti-front-production.up.railway.app
```

If this works but `www.suryadrishti.in` doesn't, it's a DNS issue.

## Contact Information

- **Railway Support:** https://railway.app/help
- **DNS Checker:** https://dnschecker.org
- **SSL Checker:** https://www.ssllabs.com/ssltest/

