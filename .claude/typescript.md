# TypeScript Rules

## Type Safety

- **Enable strict mode** in `tsconfig.json` (`"strict": true`)
- **NEVER use `any`** - use `unknown` if type is truly unknown, then narrow with type guards
- **Avoid type assertions** (`as Type`) - prefer type guards and narrowing
- **No non-null assertions** (`!`) unless absolutely certain and documented
- Prefer `undefined` over `null` for optional values (unless interfacing with APIs that use `null`)

## Type Organization

### For Simple Projects

- Store all types and interfaces in a `types.ts` file at the project root or `src/` directory

### For Complex Projects

- Create a `/types` folder with organized files:
  ```
  /types
    /api        # API request/response types
    /models     # Domain model types
    /dto        # Data transfer objects
    /common     # Shared utility types
    index.ts    # Barrel export
  ```

### React Component Props

- **Exception**: React component prop interfaces should be co-located with their components
- Name them `{ComponentName}Props`: `ButtonProps`, `UserCardProps`
- Export props interfaces for reusable components

## Type Definitions

### Prefer Interfaces for Object Shapes

```typescript
// Good
interface User {
  id: string;
  name: string;
  email: string;
}

// Use types for unions, intersections, and utility types
type Status = 'pending' | 'active' | 'inactive';
type UserWithRole = User & { role: Role };
```

### Use Discriminated Unions for State

```typescript
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };
```

### Generic Constraints

```typescript
// Constrain generics when possible
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

## Enums and Constants

### Prefer const objects over enums

```typescript
// Preferred
const Status = {
  PENDING: 'pending',
  ACTIVE: 'active',
  INACTIVE: 'inactive',
} as const;

type Status = typeof Status[keyof typeof Status];
```

### Use enums only for truly enumerable values

```typescript
// Acceptable for numeric enums
enum HttpStatus {
  OK = 200,
  NOT_FOUND = 404,
  INTERNAL_ERROR = 500,
}
```

## Functions

### Explicit Return Types for Public Functions

```typescript
// Good - explicit return type
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Arrow functions with complex logic should also have explicit return types
const processUser = (user: User): ProcessedUser => {
  // ...
};
```

### Use Function Overloads for Complex Signatures

```typescript
function parse(input: string): object;
function parse(input: Buffer): object;
function parse(input: string | Buffer): object {
  // implementation
}
```

## Async/Await

- Always use `async/await` over raw Promises with `.then()`
- Type async functions with `Promise<T>`
- Handle errors with try/catch, not `.catch()`
- Use `Promise.all()` for concurrent operations
- Use `Promise.allSettled()` when some failures are acceptable

## Imports

### Import Order

1. External libraries (node_modules)
2. Internal aliases (`@/`, `~/`)
3. Relative imports (parent directories first, then siblings)
4. Type imports (using `import type`)

```typescript
import { useState } from 'react';
import { z } from 'zod';

import { api } from '@/lib/api';
import { Button } from '@/components/ui';

import { useUser } from '../hooks';
import { formatDate } from './utils';

import type { User, ApiResponse } from '@/types';
```

### Use `import type` for Type-Only Imports

```typescript
import type { User } from '@/types';
```

## Naming Conventions

- **Interfaces**: PascalCase, noun-based: `User`, `ApiResponse`
- **Types**: PascalCase: `Status`, `RequestState`
- **Type parameters**: Single uppercase or descriptive: `T`, `TData`, `TError`
- **Files**: kebab-case: `user-service.ts`, `api-client.ts`
- **React components**: PascalCase files: `UserCard.tsx`

## Null/Undefined Handling

- Use optional chaining: `user?.address?.city`
- Use nullish coalescing: `value ?? defaultValue`
- Avoid loose equality checks; use strict equality: `===`, `!==`

## Zod for Runtime Validation

- Use Zod schemas for API responses and user input
- Infer types from Zod schemas to ensure consistency:

```typescript
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1),
});

type User = z.infer<typeof UserSchema>;
```

## ESLint and Prettier

- Use ESLint with `@typescript-eslint` plugin
- Enable recommended rules plus strict type-checking rules
- Use Prettier for formatting (no debates about style)
- Configure in `.eslintrc` and `.prettierrc`
