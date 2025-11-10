# Custom Domain Setup Guide - www.suryadrishti.in

This guide helps you configure the custom domain `www.suryadrishti.in` for your SuryaDrishti deployment on Railway.

## Railway Custom Domain Configuration

### Frontend Service (www.suryadrishti.in)

1. **In Railway Dashboard:**
   - Go to your frontend service
   - Navigate to **Settings** → **Networking**
   - You should see `www.suryadrishti.in` configured (Port 8080)
   - The domain should show "Setup complete" with a green checkmark

2. **Update Environment Variables:**
   - Go to frontend service → **Variables**
   - Update `NEXT_PUBLIC_API_URL` to point to your backend:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-domain.railway.app/api/v1
     ```
   - Or if you also have a custom domain for backend:
     ```
     NEXT_PUBLIC_API_URL=https://api.suryadrishti.in/api/v1
     ```

### Backend Service

1. **Configure Custom Domain (Optional but Recommended):**
   - Go to backend service → **Settings** → **Networking**
   - Add custom domain: `api.suryadrishti.in` (or use Railway-provided domain)
   - Note the domain URL

2. **Update CORS Settings:**
   - Go to backend service → **Variables**
   - Update `ALLOWED_ORIGINS` to include your custom domain:
     ```
     ALLOWED_ORIGINS=https://www.suryadrishti.in,https://suryadrishti.in,https://your-frontend.railway.app
     ```
   - Also update `FRONTEND_URLS`:
     ```
     FRONTEND_URLS=https://www.suryadrishti.in,https://suryadrishti.in
     ```

## DNS Configuration

### For www.suryadrishti.in

1. **Add CNAME Record:**
   - In your DNS provider (e.g., Cloudflare, Namecheap, GoDaddy)
   - Add a CNAME record:
     ```
     Type: CNAME
     Name: www
     Value: [Railway-provided domain].railway.app
     TTL: 3600
     ```

2. **Add A Record for Root Domain (Optional):**
   - If you want `suryadrishti.in` (without www) to work:
     ```
     Type: A
     Name: @
     Value: [Railway IP address]
     ```
   - Or use CNAME:
     ```
     Type: CNAME
     Name: @
     Value: www.suryadrishti.in
     ```

### SSL Certificate

Railway automatically provisions SSL certificates for custom domains via Let's Encrypt. This usually takes a few minutes after DNS propagation.

## Environment Variables Checklist

### Frontend Service Variables:
```
NEXT_PUBLIC_API_URL=https://your-backend-domain.railway.app/api/v1
```

### Backend Service Variables:
```
ALLOWED_ORIGINS=https://www.suryadrishti.in,https://suryadrishti.in,https://your-frontend.railway.app
FRONTEND_URLS=https://www.suryadrishti.in,https://suryadrishti.in
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://... (auto-set by Railway)
REDIS_URL=redis://... (if using Redis)
```

## Verification

1. **Check DNS Propagation:**
   ```bash
   nslookup www.suryadrishti.in
   ```

2. **Test Frontend:**
   - Visit `https://www.suryadrishti.in`
   - Should load the SuryaDrishti dashboard

3. **Test Backend API:**
   - Visit `https://your-backend-domain.railway.app/api/v1/health`
   - Should return `{"status": "healthy"}`

4. **Check CORS:**
   - Open browser console on `https://www.suryadrishti.in`
   - Should not see CORS errors when making API requests

## Troubleshooting

### CORS Errors
- Ensure `ALLOWED_ORIGINS` includes `https://www.suryadrishti.in`
- Ensure `FRONTEND_URLS` includes your custom domain
- Redeploy backend after updating environment variables

### DNS Not Resolving
- Wait for DNS propagation (can take up to 48 hours, usually < 1 hour)
- Check DNS records are correct
- Verify CNAME points to Railway domain

### SSL Certificate Issues
- Wait a few minutes for Let's Encrypt to provision certificate
- Check Railway logs for SSL certificate errors
- Ensure DNS is properly configured before SSL provisioning

## Next Steps

1. Update `NEXT_PUBLIC_API_URL` in frontend to use custom domain (if backend also has custom domain)
2. Update backend `ALLOWED_ORIGINS` to include custom domain
3. Redeploy both services
4. Test the application on custom domain
5. Update any hardcoded URLs in the application

## Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify DNS configuration
3. Check browser console for errors
4. Verify environment variables are set correctly

