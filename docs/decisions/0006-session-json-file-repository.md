# Use file-based session repository to enable cross-process session sharing

Date: 2025-05-29

Status: accepted

## Context

The application originally used `SessionInMemoryRepository` to store session data (user login, selected order account, item code) in memory. While suitable for the main CLI process, standalone subprocesses (such as the Order Executor) each instantiate their own in-memory repository. This isolation prevents subprocesses from reading session state set by the main process, leading to errors like "Missing order account or item code in session."

## Decision

Introduce a new `SessionJsonFileRepository`, a file-based implementation of the `SessionRepositoryInterface` that persists session state to a shared JSON file (`tmp/session.json`) in the project root. Both the main application (`app.py`) and standalone processes (`run_order_executor.py`) now use this repository. This ensures that all processes read from and write to the same session file, enabling accurate session sharing across process boundaries.

## Note on serialization bug

During implementation, directly persisting `order_account_set` (a .NET `String[]`) triggered:

    TypeError: Object of type String[] is not JSON serializable

This occurred because the repository wrote the raw `String[]` to JSON. We fixed it by converting incoming iterables to a pure Python `list[str]` in `SessionJsonFileRepository.set_order_account_set` before serialization.

## Consequences

- Session state persists to disk; subprocesses can access up-to-date session data without in-memory singletons.
- Slight file I/O overhead, but negligible for typical usage patterns.
- The `tmp/session.json` file must be writable by all processes and cleaned up when sessions expire or on application shutdown.
- Existing tests for session repositories should be updated to handle file creation and cleanup for isolation. 