## 2.2
Several bugfixes, internal improvements, and code cleanup, almost entirely by @Changaco

- Prune some remnants of Python 2 compatibility
- Prevent SMTP test failures from causing deadlocks
- Clean up and refactor message rendering
- Add a `host_id` argument to `make_msgid`
- Improve the uniqueness of generated message IDs
- Add proper timeouts to SMTP tests
