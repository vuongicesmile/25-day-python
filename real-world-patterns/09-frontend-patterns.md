# Pattern 09: Frontend Patterns — Zustand, TanStack Query, API Client

## 1. Zustand State Management

### Tại sao Zustand thay vì Redux?

| | Redux | Zustand |
|---|---|---|
| Boilerplate | Nhiều (actions, reducers, selectors) | Minimal |
| Bundle size | ~45KB | ~2.9KB |
| Learning curve | Cao | Thấp |
| DevTools | Redux DevTools | Zustand DevTools |
| Performance | Tốt | Tốt |

### Zustand store pattern từ production

```typescript
// stores/auth-store.ts
import { create } from "zustand";

interface AuthState {
  // State
  user: UserSession | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions — đặt cùng trong store, không tách reducer
  setUser: (user: UserSession) => void;
  clearUser: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  // Initial state
  user: null,
  isAuthenticated: false,
  isLoading: true,

  // Actions — update nhiều fields atomically
  setUser: (user) =>
    set({
      user,
      isAuthenticated: true,
      isLoading: false,
    }),

  clearUser: () =>
    set({ user: null, isAuthenticated: false, isLoading: false }),

  setLoading: (isLoading) => set({ isLoading }),
}));

// Sử dụng — selective subscription (chỉ re-render khi field thay đổi)
const user = useAuthStore((state) => state.user);
const isLoading = useAuthStore((state) => state.isLoading);

// Lấy action — không trigger re-render
const { setUser, clearUser } = useAuthStore.getState();
```

### Store cho streaming state

```typescript
// stores/chat-store.ts
interface StreamingState {
  content: string;
  isStreaming: boolean;
  messageId: string | null;
}

interface ChatStore {
  // Map của chatId → streaming state
  streamingByChat: Record<string, StreamingState>;

  startStreaming: (chatId: string, messageId: string) => void;
  appendContent: (chatId: string, chunk: string) => void;
  finishStreaming: (chatId: string) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  streamingByChat: {},

  startStreaming: (chatId, messageId) =>
    set((state) => ({
      streamingByChat: {
        ...state.streamingByChat,
        [chatId]: { content: "", isStreaming: true, messageId },
      },
    })),

  appendContent: (chatId, chunk) =>
    set((state) => {
      const current = state.streamingByChat[chatId];
      if (!current) return state;
      return {
        streamingByChat: {
          ...state.streamingByChat,
          [chatId]: { ...current, content: current.content + chunk },
        },
      };
    }),

  finishStreaming: (chatId) =>
    set((state) => ({
      streamingByChat: {
        ...state.streamingByChat,
        [chatId]: {
          ...state.streamingByChat[chatId],
          isStreaming: false,
        },
      },
    })),
}));
```

---

## 2. API Client với Auto-retry

```typescript
// lib/api-fetch.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";
const DEFAULT_TIMEOUT_MS = 30_000;

// In-flight deduplication (tránh double fetch khi React StrictMode)
const _inflightGets = new Map<string, { promise: Promise<unknown> }>();

export async function apiFetch<T>(
  path: string,
  options: RequestInit & {
    noAuth?: boolean;
    skipAuthRefresh?: boolean;
  } = {}
): Promise<T> {
  const method = options.method ?? "GET";

  // ── Dedup in-flight GET requests ───────────────────────────
  if (method === "GET" && !options.noAuth) {
    const cacheKey = path;
    const inflight = _inflightGets.get(cacheKey);
    if (inflight) return inflight.promise as Promise<T>;

    const promise = _doFetch<T>(path, options);
    _inflightGets.set(cacheKey, { promise });
    promise.finally(() => _inflightGets.delete(cacheKey));
    return promise;
  }

  return _doFetch<T>(path, options);
}

async function _doFetch<T>(path: string, options: any): Promise<T> {
  // ── Ensure valid access token ───────────────────────────────
  if (!options.noAuth && !options.skipAuthRefresh) {
    await ensureAccessToken(); // Refresh if expired
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(),
    DEFAULT_TIMEOUT_MS
  );

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
    ...(options.noAuth
      ? {}
      : { Authorization: `Bearer ${getAccessToken()}` }),
  };

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });

    // ── 401 → refresh → retry ONCE ─────────────────────────────
    if (response.status === 401 && !options.skipAuthRefresh) {
      await refreshAccessToken();
      const retryResponse = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers: {
          ...headers,
          Authorization: `Bearer ${getAccessToken()}`,
        },
        signal: controller.signal,
      });
      return parseResponse<T>(retryResponse);
    }

    return parseResponse<T>(response);
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Request timed out", "timeout", 408);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
```

---

## 3. TanStack Query Patterns

```typescript
// hooks/use-books.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// Query Keys — centralized để tránh typos
export const bookKeys = {
  all: ["books"] as const,
  list: (filters: BookFilters) => ["books", "list", filters] as const,
  detail: (id: string) => ["books", id] as const,
};

// List với filters
export function useBooks(filters: BookFilters) {
  return useQuery({
    queryKey: bookKeys.list(filters),
    queryFn: () => apiFetch<Book[]>(`/books?${new URLSearchParams(filters)}`),
    staleTime: 30_000,     // Cache 30s trước khi refetch
    gcTime: 5 * 60_000,   // Giữ trong memory 5 phút
  });
}

// Single item
export function useBook(id: string) {
  return useQuery({
    queryKey: bookKeys.detail(id),
    queryFn: () => apiFetch<Book>(`/books/${id}`),
    enabled: !!id,  // Không fetch khi id rỗng
  });
}

// Create mutation
export function useCreateBook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateBookData) =>
      apiFetch<Book>("/books", { method: "POST", body: JSON.stringify(data) }),

    onSuccess: (newBook) => {
      // Invalidate list → re-fetch
      queryClient.invalidateQueries({ queryKey: bookKeys.all });

      // Seed detail cache → tránh extra fetch
      queryClient.setQueryData(bookKeys.detail(newBook.id), newBook);
    },

    onError: (error: ApiError) => {
      toast.error(error.message);
    },
  });
}

// Optimistic update
export function useUpdateBook() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateBookData }) =>
      apiFetch<Book>(`/books/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),

    // Optimistic update — update UI trước khi server confirm
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: bookKeys.detail(id) });
      const previous = queryClient.getQueryData(bookKeys.detail(id));

      // Update cache ngay
      queryClient.setQueryData(bookKeys.detail(id), (old: Book) => ({
        ...old,
        ...data,
      }));

      return { previous }; // Context cho onError
    },

    onError: (_, { id }, context) => {
      // Rollback nếu server error
      if (context?.previous) {
        queryClient.setQueryData(bookKeys.detail(id), context.previous);
      }
    },

    onSettled: (_, __, { id }) => {
      // Always refetch để sync với server
      queryClient.invalidateQueries({ queryKey: bookKeys.detail(id) });
    },
  });
}
```

---

## Interview Key Points

```
1. "Zustand vs Redux?"
   - Redux: good for complex state, time-travel debugging, large teams
   - Zustand: minimal, fast, good for most React apps
   - Zustand không cần Provider, không boilerplate

2. "TanStack Query vs SWR vs manual fetch?"
   - TanStack Query: most features (mutation, optimistic, infinite scroll)
   - SWR: simpler, Vercel ecosystem
   - Manual: fine for simple cases, loses caching/dedup/background refresh

3. "Optimistic updates — when to use?"
   - Fast UI response (no waiting for server)
   - Must handle rollback on error
   - Good for: like buttons, todo toggle, form submissions
   - Bad for: anything requiring server validation (payments, auth)

4. "Request deduplication — why?"
   - React StrictMode renders twice in dev → double fetch
   - Multiple components need same data → single request
   - Store in-flight promises, share result

5. "staleTime vs gcTime?"
   - staleTime: data considered "fresh" for this long (no refetch)
   - gcTime: how long unused data stays in memory
   - staleTime=0: always refetch when component mounts
   - gcTime=Infinity: keep forever (manual invalidation only)
```
