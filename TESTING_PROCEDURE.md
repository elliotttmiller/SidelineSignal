# SidelineSignal Autonomous System Testing Procedure

This document outlines the official procedure for certifying that the autonomous feedback loop of the SidelineSignal ecosystem is stable and ready for unattended operation.

## Overview

The SidelineSignal system consists of two primary components that must work together autonomously:

1. **Signal Scout** (`signal_scout/`) - Discovers, verifies, and manages streaming sites
2. **Sideline App** (`sideline_app/`) - Provides web interface and API for monitoring sites

The autonomous loop relies on a shared SQLite database (`shared_data/sites.db`) that enables loose coupling between these components.

## Testing Methodology

### Phase 1: Environment Preparation

1. **Ensure Clean Virtual Environments**:
   ```bash
   # Scout environment setup
   python -m venv scout_venv
   source scout_venv/bin/activate  # or scout_venv\Scripts\activate on Windows
   pip install -r requirements_scout.txt
   deactivate

   # App environment setup  
   python -m venv app_venv
   source app_venv/bin/activate    # or app_venv\Scripts\activate on Windows
   pip install -r requirements_app.txt
   deactivate
   ```

2. **Verify Database State**:
   ```bash
   sqlite3 shared_data/sites.db "SELECT COUNT(*) as total_sites FROM sites;"
   sqlite3 shared_data/sites.db "SELECT COUNT(*) as active_sites FROM sites WHERE is_active = 1;"
   ```

### Phase 2: Baseline Scout Execution

Execute the Signal Scout to establish a baseline database state.

1. **Run Initial Scout Cycle**:
   ```bash
   source scout_venv/bin/activate
   cd signal_scout/
   python scout.py
   deactivate
   ```

2. **Record Baseline Metrics**:
   - Note the total number of sites discovered
   - Note the number of sites that passed verification
   - Note the final database statistics
   - Check `signal_scout/scout.log` for any errors

3. **Verify Database Population**:
   ```bash
   sqlite3 shared_data/sites.db "SELECT name, url, source, confidence_score, is_active FROM sites ORDER BY last_verified DESC LIMIT 10;"
   ```

### Phase 3: Application Integration Test

Test that the Sideline App correctly reads and processes data from the shared database.

1. **Start the Sideline Application**:
   ```bash
   source app_venv/bin/activate
   cd sideline_app/
   python app.py
   ```

2. **Verify Web Interface**:
   - Navigate to `http://localhost:5000`
   - Confirm the interface loads without errors
   - Verify that sites discovered by the Scout are displayed

3. **Test API Endpoint**:
   ```bash
   curl http://localhost:5000/api/statuses | jq .
   ```
   - Confirm JSON response includes all active sites
   - Verify `source` field shows `scout_discovery` for Scout-found sites
   - Check that status checks are performed correctly

4. **Stop the Application** (Ctrl+C)

### Phase 4: Autonomous Loop Validation (Soak Test)

This is the critical test that validates the autonomous feedback loop.

1. **Second Scout Execution** (with app data present):
   ```bash
   source scout_venv/bin/activate
   cd signal_scout/
   python scout.py
   deactivate
   ```

2. **Analyze Autonomous Behavior**:
   - **Re-verification**: Existing sites should be re-verified and updated
   - **New Discovery**: New sites may be discovered and added
   - **Self-Healing**: Previously failing sites should be deactivated if they continue to fail
   - **Database Integrity**: No duplicate entries should be created

3. **Database State Comparison**:
   ```bash
   # Check for any database inconsistencies
   sqlite3 shared_data/sites.db "SELECT url, COUNT(*) as count FROM sites GROUP BY url HAVING count > 1;"
   
   # Verify last_verified timestamps are recent
   sqlite3 shared_data/sites.db "SELECT name, url, last_verified FROM sites WHERE is_active = 1 ORDER BY last_verified DESC;"
   ```

4. **Application Re-test**:
   - Restart the Sideline App
   - Verify it reflects the updated database state
   - Test API endpoint again to confirm data consistency

### Phase 5: Extended Soak Test (Optional but Recommended)

For production deployment, run an extended test to validate long-term stability.

1. **Multiple Scout Cycles**:
   Execute the Scout 3-5 times with 5-10 minute intervals between runs:
   ```bash
   # Run this sequence multiple times
   source scout_venv/bin/activate
   cd signal_scout/
   python scout.py
   deactivate
   sleep 300  # Wait 5 minutes
   ```

2. **Monitor System Behavior**:
   - Database should remain stable and consistent
   - Log files should not show repeated errors
   - Memory usage should remain constant
   - No resource leaks should occur

### Certification Criteria

The system is certified for autonomous operation when ALL of the following conditions are met:

#### ✅ Core Functionality
- [ ] Scout successfully discovers and verifies streaming sites
- [ ] Scout stores verified sites in the shared database with proper schema
- [ ] App successfully loads and displays sites from the shared database
- [ ] API endpoint returns correct JSON data for all active sites

#### ✅ Autonomous Loop Stability  
- [ ] Scout re-verifies existing sites without creating duplicates
- [ ] Scout updates `last_verified` timestamps correctly
- [ ] Scout deactivates persistently failing sites (self-healing)
- [ ] App reflects database changes without requiring restart

#### ✅ Data Integrity
- [ ] No duplicate URLs exist in the database
- [ ] All active sites have recent `last_verified` timestamps
- [ ] Confidence scores are reasonable (> 0 for active sites)
- [ ] Database schema remains consistent across all operations

#### ✅ Error Handling
- [ ] Scout handles network failures gracefully
- [ ] Scout logs errors appropriately without crashing
- [ ] App handles empty database states gracefully
- [ ] App provides fallback behavior when database is unavailable

#### ✅ Resource Management
- [ ] Memory usage remains stable across multiple Scout executions
- [ ] Log files don't grow excessively
- [ ] No hanging processes or connections
- [ ] Database file size grows predictably

## Troubleshooting

### Common Issues

**Issue**: Scout discovers 0 URLs
**Solution**: Check network connectivity and `scout_config.json` parameters

**Issue**: App shows fallback sites instead of Scout-discovered sites
**Solution**: Verify database file exists and has proper permissions

**Issue**: Duplicate sites in database
**Solution**: Check Scout's URL deduplication logic and database constraints

**Issue**: All sites show as "Offline" 
**Solution**: Verify network connectivity from app environment

### Log Analysis

Monitor these key log files:
- `signal_scout/scout.log` - Scout execution logs
- `sideline_app/status_changes.log` - Site status change history

### Recovery Procedures

If the system fails certification:
1. Review all log files for error patterns
2. Reset the database by deleting `shared_data/sites.db` (it will be recreated)
3. Check virtual environment dependencies
4. Re-run the testing procedure from Phase 1

## Conclusion

This testing procedure ensures that the SidelineSignal system can operate autonomously without human intervention. Once certified, the system can be deployed to production with confidence that it will maintain itself and provide reliable monitoring services.

The autonomous loop (Scout → Database → App → Scout) is the core of the system's self-sustaining nature, and this testing procedure validates that loop thoroughly.