# Heatmap Deployment Checklist

Use this checklist when deploying the heatmap to production.

## Pre-Deployment

### Environment Check
- [ ] WebSocket server tests pass: `cd syngex && python3 -m pytest tests/test_websocket_server.py -v`
- [ ] All ports available (8201, 8202): `lsof -i :8201` and `lsof -i :8202`
- [ ] Python 3.8+ available: `python3 --version`
- [ ] Required packages installed: `pip3 list | grep -E "fastapi|uvicorn|websockets"`

### Backup
- [ ] Current state backed up: `git status` (check for uncommitted changes)
- [ ] Git commit made: `git add . && git commit -m "Pre-heatmap deployment backup"`
- [ ] Tag created: `git tag -a heatmap-pre-deployment -m "Pre-deployment backup"`

### Documentation Review
- [ ] Read `HEATMAP_IMPLEMENTATION_PLAN.md`
- [ ] Reviewed `STARTUP.md` procedures
- [ ] Familiar with `QUICK_REFERENCE.md`

## Deployment

### Step 1: Start Services
- [ ] Run startup script: `./scripts/start-heatmap.sh`
- [ ] OR start manually (see STARTUP.md)

### Step 2: Verify Services
- [ ] WebSocket health check passes: `curl http://localhost:8202/health`
- [ ] Frontend loads: `curl http://localhost:8201/index.html | head -5`
- [ ] No errors in startup logs

### Step 3: Browser Verification
- [ ] Open http://localhost:8201 in browser
- [ ] WebSocket status shows green (connected)
- [ ] No console errors (F12 → Console)
- [ ] All panels render correctly:
  - [ ] Header displays symbol and price
  - [ ] Profile tabs are visible
  - [ ] Risk metrics panel shows data
  - [ ] Dominant levels heatmap shows strikes
  - [ ] Strategy grid has 42 cells
  - [ ] Log stream has entries

### Step 4: Data Flow Verification
- [ ] Open DevTools → Network → WS tab
- [ ] WebSocket connection established to `ws://localhost:8202/ws`
- [ ] Messages being received (check traffic)
- [ ] Data updates in real-time
- [ ] Subscribe message sent: `{"type":"subscribe","channels":[...]}`

### Step 5: Functionality Testing
- [ ] Profile tab switching works
- [ ] Strategy cell selection works (click to highlight)
- [ ] Log filter buttons work (All/Signal/Alert/GEX/Flow)
- [ ] Hover effects work on panels
- [ ] No JavaScript errors in console

## Post-Deployment

### Auto-Start Configuration
- [ ] systemd service created (optional): `sudo systemctl enable syngex-heatmap`
- [ ] OR startup script added to `.bashrc`
- [ ] Test auto-start: reboot and verify services start

### Monitoring Setup
- [ ] Health check script created: `scripts/monitor-heatmap.sh`
- [ ] Logs accessible (console or file)
- [ ] Alerting configured (if needed)

### Documentation
- [ ] Runbook updated with heatmap procedures
- [ ] Team notified of deployment (if applicable)
- [ ] This checklist completed and dated

## Validation

### Performance Check
- [ ] Update latency < 100ms (measure in DevTools)
- [ ] Memory usage < 100MB (DevTools → Memory)
- [ ] CPU usage < 5% (DevTools → Performance)

### Reconnection Test
- [ ] Stop WebSocket server: `pkill -f websocket_server`
- [ ] Verify frontend shows disconnected (red indicator)
- [ ] Restart WebSocket server
- [ ] Verify frontend auto-reconnects (green indicator)
- [ ] Check reconnection logged in console

### Error Handling Test
- [ ] Invalid message format doesn't crash frontend
- [ ] Missing data uses fallback values
- [ ] UI remains responsive during errors

## Sign-Off

### User Acceptance
- [ ] Hologaun reviews dashboard
- [ ] All requirements met
- [ ] Approved for production use

### Final Steps
- [ ] Remove backup tag if stable after 24h: `git tag -d heatmap-pre-deployment`
- [ ] Update operational runbook
- [ ] Close deployment ticket/task

---

## Rollback Procedure

If issues are found, rollback immediately:

```bash
# 1. Stop new heatmap
pkill -f "http.server 8201"
pkill -f "websocket_server"

# 2. Restore old dashboard (if needed)
cd /home/hologaun/.openclaw/workspace/forge
git checkout heatmap-pre-deployment -- dashboard/app.py dashboard/client.py

# 3. Restart old dashboard
python3 dashboard/app.py

# 4. Verify old dashboard works
open http://localhost:8200  # or original port
```

## Issues Log

| Date | Issue | Resolution | Status |
|------|-------|------------|--------|
| | | | |
| | | | |

---

**Deployed By**: _______________  
**Date**: _______________  
**Approved By**: _______________  
**Notes**: _________________________________________________
