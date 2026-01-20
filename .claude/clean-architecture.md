# Clean Architecture Rules

## Core Principle: The Dependency Rule

**Dependencies must point inward.** Inner layers must not know anything about outer layers.

```
┌─────────────────────────────────────────────────────────┐
│                  Frameworks & Drivers                   │
│  (Web, UI, DB, External APIs, Devices)                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Interface Adapters                  │   │
│  │  (Controllers, Gateways, Presenters)            │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │            Application Layer             │   │   │
│  │  │         (Use Cases / Services)           │   │   │
│  │  │  ┌─────────────────────────────────┐   │   │   │
│  │  │  │         Domain Layer            │   │   │   │
│  │  │  │    (Entities, Value Objects)    │   │   │   │
│  │  │  └─────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## The Four Layers

### 1. Domain Layer (Entities)

The innermost layer containing enterprise business rules.

**Contains:**
- Entities (core business objects)
- Value Objects (immutable objects defined by their attributes)
- Domain Events
- Domain Exceptions

**Rules:**
- No dependencies on outer layers
- No framework code
- No infrastructure concerns
- Pure business logic only

```typescript
// domain/entities/user.ts
export class User {
  constructor(
    public readonly id: UserId,
    public readonly email: Email,
    public name: string,
    private _status: UserStatus
  ) {}

  activate(): void {
    if (this._status === UserStatus.BANNED) {
      throw new UserBannedError(this.id);
    }
    this._status = UserStatus.ACTIVE;
  }
}

// domain/value-objects/email.ts
export class Email {
  private constructor(private readonly value: string) {}

  static create(email: string): Email {
    if (!this.isValid(email)) {
      throw new InvalidEmailError(email);
    }
    return new Email(email);
  }

  private static isValid(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}
```

### 2. Application Layer (Use Cases)

Contains application-specific business rules.

**Contains:**
- Use Cases / Application Services
- Input/Output DTOs (Data Transfer Objects)
- Repository Interfaces (Ports)
- External Service Interfaces

**Rules:**
- Orchestrates domain entities
- Defines interfaces that outer layers implement
- No direct dependencies on infrastructure
- One use case = one action

```typescript
// application/use-cases/create-user.ts
export class CreateUserUseCase {
  constructor(
    private readonly userRepository: IUserRepository,
    private readonly emailService: IEmailService
  ) {}

  async execute(input: CreateUserInput): Promise<CreateUserOutput> {
    const email = Email.create(input.email);

    const existingUser = await this.userRepository.findByEmail(email);
    if (existingUser) {
      throw new UserAlreadyExistsError(email);
    }

    const user = User.create({
      email,
      name: input.name,
    });

    await this.userRepository.save(user);
    await this.emailService.sendWelcomeEmail(user);

    return { userId: user.id.value };
  }
}

// application/ports/user-repository.ts
export interface IUserRepository {
  findById(id: UserId): Promise<User | null>;
  findByEmail(email: Email): Promise<User | null>;
  save(user: User): Promise<void>;
  delete(id: UserId): Promise<void>;
}
```

### 3. Interface Adapters Layer

Converts data between use cases and external formats.

**Contains:**
- Controllers (handle HTTP requests)
- Presenters (format responses)
- Gateways (implement repository interfaces)
- Mappers (convert between layers)

**Rules:**
- Implements interfaces defined in Application layer
- Converts external data to domain objects
- Converts domain objects to external formats
- No business logic

```typescript
// adapters/controllers/user-controller.ts
export class UserController {
  constructor(private readonly createUserUseCase: CreateUserUseCase) {}

  async create(req: Request, res: Response): Promise<void> {
    const input: CreateUserInput = {
      email: req.body.email,
      name: req.body.name,
    };

    const output = await this.createUserUseCase.execute(input);

    res.status(201).json({
      id: output.userId,
      message: 'User created successfully',
    });
  }
}

// adapters/repositories/prisma-user-repository.ts
export class PrismaUserRepository implements IUserRepository {
  constructor(private readonly prisma: PrismaClient) {}

  async findById(id: UserId): Promise<User | null> {
    const data = await this.prisma.user.findUnique({
      where: { id: id.value },
    });

    return data ? UserMapper.toDomain(data) : null;
  }

  async save(user: User): Promise<void> {
    const data = UserMapper.toPersistence(user);
    await this.prisma.user.upsert({
      where: { id: data.id },
      create: data,
      update: data,
    });
  }
}
```

### 4. Frameworks & Drivers Layer

The outermost layer with all external concerns.

**Contains:**
- Web frameworks (Express, FastAPI, NestJS)
- Database clients (Prisma, TypeORM, SQLAlchemy)
- External APIs
- UI frameworks

**Rules:**
- All framework-specific code lives here
- Easily replaceable
- Configuration and setup
- Dependency injection container

## Key Patterns

### Repository Pattern

Abstracts data persistence behind an interface.

```typescript
// Port (Application Layer)
interface IOrderRepository {
  findById(id: OrderId): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

// Adapter (Infrastructure Layer)
class PostgresOrderRepository implements IOrderRepository {
  // Implementation details hidden from domain
}
```

### Dependency Injection

Inject dependencies rather than creating them.

```typescript
// Bad - tight coupling
class UserService {
  private repo = new PostgresUserRepository();
}

// Good - dependency injection
class UserService {
  constructor(private readonly repo: IUserRepository) {}
}
```

### DTOs (Data Transfer Objects)

Use DTOs to cross layer boundaries.

```typescript
// Input DTO
interface CreateOrderInput {
  customerId: string;
  items: Array<{ productId: string; quantity: number }>;
}

// Output DTO
interface CreateOrderOutput {
  orderId: string;
  total: number;
  status: string;
}
```

## Folder Structure

### TypeScript/Node.js

```
/src
  /domain
    /entities
    /value-objects
    /events
    /errors
  /application
    /use-cases
    /ports          # Interfaces
    /dtos
  /adapters
    /controllers
    /repositories
    /mappers
    /presenters
  /infrastructure
    /database
    /http
    /services
  /config
  main.ts           # Composition root
```

### Python

```
/src
  /domain
    /entities
    /value_objects
    /events
    /errors
  /application
    /use_cases
    /ports
    /dtos
  /adapters
    /api
    /repositories
    /mappers
  /infrastructure
    /database
    /http_client
    /services
  /config
  main.py
```

## Testing Strategy

### Unit Tests
- Test domain entities and value objects in isolation
- Test use cases with mocked repositories

### Integration Tests
- Test repository implementations against real databases
- Test API endpoints

### E2E Tests
- Test complete user flows

```typescript
// Unit test for use case
describe('CreateUserUseCase', () => {
  it('should create a user', async () => {
    const mockRepo = { save: vi.fn(), findByEmail: vi.fn() };
    const mockEmail = { sendWelcomeEmail: vi.fn() };

    const useCase = new CreateUserUseCase(mockRepo, mockEmail);

    const result = await useCase.execute({
      email: 'test@test.com',
      name: 'Test',
    });

    expect(result.userId).toBeDefined();
    expect(mockRepo.save).toHaveBeenCalled();
  });
});
```

## Common Violations to Avoid

1. **Domain depending on infrastructure**
   - Domain entities importing database models
   - Business logic checking HTTP status codes

2. **Use cases knowing about HTTP**
   - Returning Response objects from use cases
   - Throwing HTTP-specific errors

3. **Skipping layers**
   - Controllers directly accessing repositories
   - UI directly calling database

4. **Anemic domain models**
   - Entities that are just data holders
   - Business logic scattered in services

5. **Leaking infrastructure**
   - ORM models used as domain entities
   - Database IDs exposed in API responses
