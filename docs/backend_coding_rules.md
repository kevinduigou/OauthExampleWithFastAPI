- When doing structural modification to the application, use clear separation of concern between the layers:
  - Domain: Core business logic. Immutable, pure. No DB, I/O, or HTTP code.
  - Application: Use cases, orchestration.
  - Infrastructure: using DBs, APIs, or I/O.
  - Interface: Nicegui frontend.

- Immutability First:
   - Treat all function parameters as **immutable** by default. Never modify inputs directly.
   - Prefer pure functions and immutable objects with `@final` and `__slots__`.
   - Infrastructure may contain mutable functions.
   - Entities object must be mutable
   - Prefer using tuple (immutable) over list (mutable)

- Make Illegal States Unrepresentable:
  - Domain objects must not allow invalid construction.
  - Use factory methods like `try_create()` or validation before instantiation.
  - Never expose public constructors for domain objects with constraints.
- Be Explicit:
   - No dynamic behavior or magic number (e.g., metaclasses, monkey patching, decorators that inject logic).
   - Function and variable names shall be as explicit as possible. Dot not use variables names which are one letter.

- Keep Domain Objects simple dataclass (Entities mutable, Value Object and Event immutable).
  Don't use try_create function to instantiate object if there is no explicit way to not accept creation.

- Rust-style Control Flow:
  - Do not use `try`, `except`, or `raise`
  - Only infrastructure layer may contain try except around I/O operations
  - Use library result (already installed in the project):
   from result import Result, Ok, Err

    def divide(a: int, b: int) -> Result[int, str]:
        if b == 0:
            return Err("Cannot divide by zero")
        return Ok(a // b)

    values = [(10, 0), (10, 5)]
    for a, b in values:
        match divide(a, b):
            case Ok(value):
                print(f"{a} // {b} == {value}")
            case Err(e):
                print(e)

- Long Running Use cases/ tasks are:
    - Executed by a rq worker (docker/Dockerfile.worker)
    - Located under backend/application/commands_async or backend/application/querry_async
    - In the interface long running job are enqueued thanks to
      Example
      result = self._rq_client.enqueue_job(
          "backend.commands_async.load_kb_campaigns.execute_load_kb_campaigns_job",
          irma_base_url,
          self._db_url,
          job_timeout=7200,  # 2 hours timeout
      )
      And then monitor with a timer checking frequently status and metadata
      status_result = self._rq_client.get_job_status(self._job_id)
      meta_result = self._rq_client.get_job_meta(self._job_id)


- Do not allow domain objects to depend on external libraries, ORMs, or I/O.

- Use Infrastructure objects in the Application layer (don't use Port/Adapter which could over complexify design of this basic Application)
-
- Application Layer is the home of use cases which can be distinguish between commands (mutate states) and query (don't mutate states).

- Unit Tests with pytest shall be focused on domain spcific functions
-
- Integration tests shall be done with behave library (already installed)
  Beahve tests ar located under ./features

- When a modification is done on Python files, always perform
uv run pytest
uv run ruff check
uv run mypy

and finish by
uv run ruff format

to ensure that there is no errors remaining
