# SECURITY WARNING - TEMPORARY AUTHENTICATION

## ⚠️ IMPORTANT: Development Only Solution

The current implementation temporarily stores authentication credentials in the session JSON file to allow the order executor process to authenticate with the exchange API. 

**THIS IS INSECURE AND MUST NOT BE USED IN PRODUCTION!**

## Current Issues

1. **Password Storage**: User passwords are temporarily stored in plain text in `session.json`
2. **File Access**: Any process with file system access can read credentials
3. **No Encryption**: Credentials are not encrypted

## Production Solutions

For production deployment, implement one of these secure alternatives:

### 1. Token-Based Authentication
- Main app obtains authentication token from exchange
- Token is stored (with short expiry) instead of password
- Order executor uses token for API calls

### 2. Credential Service
- Use a secure credential management service (e.g., HashiCorp Vault, AWS Secrets Manager)
- Order executor retrieves credentials from secure service
- Credentials never touch disk

### 3. Process Architecture Change
- Run order executor as a thread within main process instead of separate process
- Share authenticated API client instance
- Eliminates need for separate authentication

### 4. Message Queue with Authentication
- Main app places authenticated orders via message queue
- Order executor only handles order status updates
- No direct order placement from executor

## Temporary Cleanup

The temporary auth details are:
- Stored when user logs in via main app
- Cleared when user logs out
- Should be manually deleted if app crashes

To manually clear credentials:
```bash
# Remove the session file
rm session.json
```

## Implementation Location

Temporary code is marked with warnings in:
- `src/infrastructure/repositories/session_json_file_repository.py`
- `src/interactor/use_cases/user_login.py`
- `src/interactor/use_cases/user_logout.py`
- `run_order_executor.py` 