# Trade-offs and Limitations

### Known limitations

**Single scan constraint**

- Limits throughput
- Simplifies consistency

**At-least-once execution**

- Duplicate execution possible
- Handled via idempotency

**No distributed locking**

- Relies on DB checks

**AWS rate limits**

- Parallel scans may hit limits

**Batch scanning only**

- No real-time monitoring

### Possible improvements

- Multi-account support
- Distributed workers
- Incremental scanning
- UI dashboard
