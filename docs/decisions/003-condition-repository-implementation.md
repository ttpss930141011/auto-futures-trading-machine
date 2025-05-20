# Condition Repository Implementation Strategy

Date: 2024-03-19

Status: accepted

## Context

The futures trading system consists of multiple processes:
- Main CLI process for user interaction and configuration
- Strategy process for market analysis
- Order Executor process for trade execution

Initially, we used `ConditionInMemoryRepository` for storing trading conditions, but this led to several issues:
1. Data isolation between processes - conditions created in CLI weren't visible to Strategy
2. Data persistence - conditions were lost on process restart
3. Race conditions when multiple processes tried to access/modify conditions

## Decision

We will implement the repository pattern in three phases:

### Phase 1 (Current): JsonFileRepository
Implement `ConditionJsonFileRepository` that:
- Persists conditions to a JSON file on disk
- Allows all processes to share the same data
- Provides basic data persistence
- Maintains simple implementation for early development

### Phase 2 (Future): SQLite Implementation
Plan to migrate to SQLite when we need:
- Better concurrency control
- Transaction support
- Complex queries
- Data integrity constraints
- Migration management

### Phase 3 (Optional): Full Database
Consider migration to PostgreSQL/MySQL if we need:
- Multi-machine deployment
- High concurrency
- Advanced backup/replication
- Complex reporting

## Technical Details

### JsonFileRepository Implementation
```python
class ConditionJsonFileRepository(ConditionRepositoryInterface):
    def __init__(self, file_path: str | None = None):
        self._file_path = file_path or self.DEFAULT_FILENAME
        self._data: Dict[uuid.UUID, Condition] = {}
        self._load()  # Load existing data on initialization
```

### Key Features
1. File-based persistence
2. JSON serialization/deserialization
3. Shared access across processes
4. Automatic data loading on startup

## Consequences

### Positive
1. All processes can now share trading conditions
2. Conditions persist between program restarts
3. Simple implementation, easy to debug
4. No external dependencies (just Python stdlib)
5. Easy to backup (just copy the JSON file)

### Negative
1. No built-in concurrency control (potential race conditions)
2. Limited query capabilities
3. No transaction support
4. Need to handle JSON serialization edge cases
5. File I/O overhead on every operation

### Risks
1. Race conditions during concurrent writes
2. File corruption if process crashes during write
3. Performance impact with large datasets
4. No automatic schema migration

## Mitigation Strategies

1. Consider implementing file locking for write operations
2. Add periodic backup of the JSON file
3. Monitor file size and performance
4. Plan for SQLite migration when needed

## Future Considerations

1. Monitor system performance and data volume
2. Watch for concurrent access issues
3. Consider implementing a caching layer
4. Prepare SQLite migration plan
5. Document upgrade path for users 