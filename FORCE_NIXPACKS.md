# Force Railway to Use Nixpacks (Not Docker)

## ✅ What I Just Did

1. **Renamed `Dockerfile` to `Dockerfile.backup`** - Railway won't auto-detect it anymore
2. **Updated `railway.json`** - Explicitly tells Railway to use Nixpacks
3. **Updated `nixpacks.toml`** - Proper Nixpacks configuration

## 🚀 What Happens Now

Railway will now:
- ✅ Use **Nixpacks** builder (not Docker)
- ✅ Auto-detect Node.js from `package.json`
- ✅ Use `nixpacks.toml` for build configuration
- ✅ Build with: `npm ci && npm run build`
- ✅ Start with: `npm start`

## 📋 Verify in Railway

After the next deploy, check the build logs. You should see:
```
Using Nixpacks
==============
```

NOT:
```
Using Dockerfile
```

## 🔧 If Railway Still Uses Docker

1. **Go to your frontend service** in Railway
2. **Settings** → **Build** tab
3. **Manually set Builder to "Nixpacks"**
4. **Save and redeploy**

## 📝 Railway Service Settings

**Frontend Service:**
- Root Directory: `frontend`
- Builder: **Nixpacks** (should auto-detect now)
- Build Command: (leave empty, uses nixpacks.toml)
- Start Command: `npm start`

The Dockerfile is now renamed to `Dockerfile.backup` so Railway won't find it and will use Nixpacks instead.

