# Python Coder Practice Reference

Use these examples as style guidance, not universal law. Prefer existing repository conventions when they are clear.

## Boundary-Friendly Service

Good:
```python
from dataclasses import dataclass
from typing import Protocol

class UserRepository(Protocol):
    def get_by_email(self, email: str) -> "User | None": ...
    def save(self, user: "User") -> None: ...

class PasswordHasher(Protocol):
    def hash(self, raw_password: str) -> str: ...

@dataclass(frozen=True)
class RegisterUser:
    users: UserRepository
    passwords: PasswordHasher

    def execute(self, email: str, password: str) -> "User":
        if self.users.get_by_email(email) is not None:
            raise UserAlreadyExists(email)

        user = User(email=email, password_hash=self.passwords.hash(password))
        self.users.save(user)
        return user
```

Why it is good:
- Business workflow is not tied to FastAPI, Django, SQLAlchemy, or Redis.
- External behavior is expressed as dependencies.
- The service is easy to unit test.

Avoid:
```python
def register_user(request, db):
    data = request.json()
    existing = db.execute(f"select * from users where email = '{data['email']}'")
    ...
```

Why to avoid:
- Framework request, persistence, validation, SQL, and business behavior are tangled.
- SQL injection risk appears.
- The function is hard to test outside the web framework.

## Thin Handler

Good:
```python
@router.post("/users", response_model=UserResponse)
def create_user(payload: CreateUserRequest, service: RegisterUser = Depends(get_register_user)) -> UserResponse:
    user = service.execute(email=payload.email, password=payload.password)
    return UserResponse.from_domain(user)
```

Why it is good:
- Handler validates and maps boundary objects.
- Application behavior lives in a service.
- Response mapping is explicit.

## Repository Adapter

Good:
```python
class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        row = self._session.scalar(select(UserRow).where(UserRow.email == email))
        return None if row is None else row.to_domain()

    def save(self, user: User) -> None:
        self._session.add(UserRow.from_domain(user))
```

Why it is good:
- ORM details stay in infrastructure.
- Domain model does not need a session.
- Conversion is isolated.

## No `global` State

Good:
```python
def add_metric(metrics: dict[str, int], name: str) -> None:
    metrics[name] = metrics.get(name, 0) + 1
```

Avoid:
```python
_metrics: dict[str, int] = {}

def add_metric(name: str) -> None:
    global _metrics
    _metrics[name] = _metrics.get(name, 0) + 1
```

Why to avoid:
- The dependency is hidden, so callers cannot tell what the function mutates.
- Tests leak state into each other unless they reset the module.
- Concurrency and lifecycle bugs become invisible.

If a process-wide value is genuinely required, inject it explicitly (a small
state object, a repository, a client) and keep the mutable instance at the
composition root. Do not reach for `global` to make a helper convenient.

## No Type-Checker Silencing

Good:
```python
def parse_user(payload: object) -> User:
    if not isinstance(payload, dict):
        raise ValueError("user payload must be an object")
    email = payload.get("email")
    if not isinstance(email, str):
        raise ValueError("user email must be a string")
    return User(email=email)
```

Avoid:
```python
from typing import cast

def parse_user(payload: object) -> User:
    data = cast(dict[str, str], payload)  # type: ignore[redundant-cast]
    return User(email=data["email"])
```

Why to avoid:
- `cast` asserts a type at compile time without checking at runtime.
- `# type: ignore` hides the next real error at the same line, including future
  refactors.
- Validating at the boundary gives callers a real error instead of a crash later.

Use `cast` only where an external library or protocol forces it, keep the call
next to the runtime check that justifies it, and leave a short comment naming
the boundary. Prefer `TypeGuard`, `Protocol`, generics, `TypedDict`, or a
validated parser otherwise.

## Explicit Errors

Good:
```python
class UserAlreadyExists(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"user already exists: {email}")
        self.email = email
```

Avoid returning `None`, `False`, or string codes for meaningful domain failure when callers need to distinguish causes.

## Async Boundary

Good:
```python
async def fetch_profile(client: httpx.AsyncClient, user_id: str) -> Profile:
    response = await client.get(f"/profiles/{user_id}", timeout=5.0)
    response.raise_for_status()
    return Profile.model_validate(response.json())
```

Avoid:
```python
async def fetch_profile(user_id: str) -> dict:
    return requests.get(f"https://example.com/{user_id}").json()
```

Why to avoid:
- Blocking I/O inside async code can stall the event loop.
- No timeout or validation.

## Transaction Boundary

Good:
```python
def handle(command: CreateOrder, unit_of_work: UnitOfWork) -> OrderId:
    with unit_of_work:
        order = Order.create(command.customer_id, command.items)
        unit_of_work.orders.save(order)
        unit_of_work.events.publish(order.events)
        unit_of_work.commit()
        return order.id
```

Why it is good:
- Transaction lifetime is visible.
- State changes and event publication can be coordinated.

## Test Shape

Good:
```python
def test_register_user_rejects_existing_email() -> None:
    users = FakeUserRepository([User(email="a@example.com", password_hash="hash")])
    service = RegisterUser(users=users, passwords=FakePasswordHasher())

    with pytest.raises(UserAlreadyExists):
        service.execute("a@example.com", "secret")
```

Why it is good:
- Tests behavior without a web server or database.
- Failure mode is explicit.

## Naming

Prefer:
- `CreateOrder`, `RegisterUser`, `SendInvoice`, `SqlAlchemyOrderRepository`, `HttpPaymentGateway`.

Avoid:
- `OrderManager`, `UserHelper`, `common_utils`, `process_data` when a specific responsibility exists.
