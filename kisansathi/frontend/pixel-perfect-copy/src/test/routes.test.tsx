/**
 * Route smoke tests — KisanSathi
 *
 * Renders <App /> at every declared route and asserts the page mounts without
 * throwing and without falling through to the 404 page. This is the guard that
 * catches a route pointing at a deleted/renamed page component — the exact
 * failure that broke `/market` when MarketPricePage.tsx went missing while its
 * import stayed in App.tsx.
 */

import { render, screen, waitFor, cleanup } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";

/** Routes reachable without a login token. */
const PUBLIC_ROUTES = [
  "/",
  "/about",
  "/chatbot",
  "/shop",
  "/gallery",
  "/testimonial",
  "/schemes",
  "/faq",
  "/services",
  "/crop",
  "/resources",
  "/auth",
  "/tts-test",
  "/market",
  "/weather-test",
  "/weather-debug",
];

/** Routes wrapped in <ProtectedRoute>; rendered with a token present. */
const PROTECTED_ROUTES = [
  "/seasonal-crop",
  "/fertilizer",
  "/disease",
  "/weather",
  "/soil-analysis",
  "/reminders",
  "/voice-assistant",
  "/dashboard",
  "/profile",
  "/farm-profile",
  "/livestock",
  "/community",
  "/monitoring",
  "/files",
];

/** Browser APIs jsdom lacks that page components touch on mount. */
function stubBrowserAPIs() {
  const noopObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
    takeRecords() {
      return [];
    }
  };
  vi.stubGlobal("IntersectionObserver", noopObserver);
  vi.stubGlobal("ResizeObserver", noopObserver);

  vi.stubGlobal("scrollTo", () => {});
  Object.defineProperty(window, "speechSynthesis", {
    writable: true,
    configurable: true,
    value: {
      speak: () => {},
      cancel: () => {},
      pause: () => {},
      resume: () => {},
      getVoices: () => [],
      addEventListener: () => {},
      removeEventListener: () => {},
    },
  });

  const SpeechRecognitionStub = class {
    start() {}
    stop() {}
    abort() {}
    addEventListener() {}
    removeEventListener() {}
  };
  vi.stubGlobal("SpeechRecognition", SpeechRecognitionStub);
  vi.stubGlobal("webkitSpeechRecognition", SpeechRecognitionStub);
}

/**
 * Every page fetches on mount. Return a shape that satisfies the common
 * `{ success, ... }` contract so components take their happy path instead of
 * their error branch — we are testing that pages mount, not the API.
 */
function stubFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            success: true,
            timestamp: "2026-01-01T00:00:00Z",
            prices: [],
            data: {},
            posts: [],
            files: [],
            reminders: [],
            notifications: [],
          }),
        text: () => Promise.resolve(""),
      }),
    ),
  );
}

/** Renders App at `path` and fails on any render-time exception. */
async function renderRoute(path: string) {
  window.history.pushState({}, "", path);
  const errors: unknown[] = [];
  const spy = vi.spyOn(console, "error").mockImplementation((...args) => {
    errors.push(args[0]);
  });
  try {
    render(<App />);
    // Let mount effects and the ProtectedRoute auth check settle.
    await waitFor(() => {
      expect(document.body.textContent).not.toBe("");
    });
  } finally {
    spy.mockRestore();
  }
  return errors;
}

describe("application routes", () => {
  beforeEach(() => {
    stubBrowserAPIs();
    stubFetch();
    localStorage.clear();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it.each(PUBLIC_ROUTES)("renders %s without hitting the 404 page", async (path) => {
    await renderRoute(path);
    expect(screen.queryByText(/404/)).toBeNull();
  });

  it.each(PROTECTED_ROUTES)("renders %s for a logged-in user", async (path) => {
    localStorage.setItem("token", "test-token");
    localStorage.setItem("user_name", "Test Farmer");

    await renderRoute(path);

    expect(screen.queryByText(/404/)).toBeNull();
    // A redirect to /auth would mean ProtectedRoute rejected our token.
    expect(window.location.pathname).toBe(path);
  });

  it("sends an unauthenticated visitor from a protected route to /auth", async () => {
    await renderRoute("/dashboard");
    await waitFor(() => {
      expect(window.location.pathname).toBe("/auth");
    });
  });

  it("shows the 404 page for an unknown route", async () => {
    await renderRoute("/this-route-does-not-exist");
    expect(screen.getByText(/404/)).toBeTruthy();
  });
});
