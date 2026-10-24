export interface ApiError {
  code: string;
  message: string;
  field_errors?: Record<string, string>;
  request_id?: string;
  details?: Record<string, any>;
}

export class ApiException extends Error {
  code: string;
  field_errors: Record<string, string>;
  details: Record<string, any>;

  constructor(error: ApiError) {
    super(error.message);
    this.name = "ApiException";
    this.code = error.code;
    this.field_errors = error.field_errors || {};
    this.details = error.details || {};
  }
}

let csrfTokenCache: string | null = null;

export function setCsrfToken(token: string | null) {
  csrfTokenCache = token;
}

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");

  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (csrfTokenCache && options.method && !["GET", "HEAD"].includes(options.method.toUpperCase())) {
    headers.set("X-CSRF-Token", csrfTokenCache);
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
    credentials: "include", // send session cookie
  });

  if (!response.ok) {
    let errBody: any;
    try {
      errBody = await response.json();
    } catch {
      throw new ApiException({
        code: `HTTP_${response.status}`,
        message: response.statusText || "Network request failed",
      });
    }

    if (errBody && errBody.error) {
      throw new ApiException(errBody.error);
    } else {
      throw new ApiException({
        code: `HTTP_${response.status}`,
        message: errBody.detail || "Request failed",
      });
    }
  }

  return response.json() as Promise<T>;
}
