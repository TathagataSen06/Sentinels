// Thin client for the Sentinels FastAPI backend.
//
// NOTE: For the demo this authenticates with a configured service account so
// the dashboard works out of the box. A production deployment should replace
// this with a real login page / OIDC flow and never embed credentials in the
// frontend bundle.

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DEMO_USER = process.env.NEXT_PUBLIC_DEMO_USER || 'admin@sentinels.local';
const DEMO_PASSWORD = process.env.NEXT_PUBLIC_DEMO_PASSWORD || 'changeme';

let tokenPromise: Promise<string> | null = null;

async function fetchToken(): Promise<string> {
  const body = new URLSearchParams({ username: DEMO_USER, password: DEMO_PASSWORD });
  const res = await fetch(`${API_URL}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!res.ok) throw new Error(`Authentication failed (${res.status})`);
  const data = await res.json();
  return data.access_token as string;
}

function getToken(): Promise<string> {
  if (!tokenPromise) tokenPromise = fetchToken();
  return tokenPromise;
}

async function authedFetch(path: string, init: RequestInit, token: string) {
  return fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(init.headers || {}),
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  let token = await getToken();
  let res = await authedFetch(path, init, token);

  // Token likely expired — drop the cached token and retry once.
  if (res.status === 401) {
    tokenPromise = null;
    token = await getToken();
    res = await authedFetch(path, init, token);
  }

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`);
  }
  return res.json() as Promise<T>;
}

// --- Types -------------------------------------------------------------------
export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface ApiIncident {
  id: string;
  tenant_id: string;
  source_ip: string;
  title: string;
  severity: Severity;
  severity_score: number;
  status: string;
  assignee: string | null;
  sensor_name: string | null;
  mitre: string[];
  event_count: number;
  first_seen: string;
  last_seen: string;
}

export interface IncidentEvent {
  time: string;
  event_type: string;
  plugin: string;
  technique_id: string;
  tactic: string;
  severity: number;
}

export interface ApiIncidentDetail extends ApiIncident {
  events: IncidentEvent[];
}

export interface CursorPage<T> {
  items: T[];
  next_cursor: string | null;
}

// --- Endpoints ---------------------------------------------------------------
export const fetchIncidents = () =>
  apiFetch<CursorPage<ApiIncident>>('/api/v1/incidents?limit=50');

export const fetchIncident = (id: string) =>
  apiFetch<ApiIncidentDetail>(`/api/v1/incidents/${id}`);

export const updateIncident = (
  id: string,
  body: { status?: string; assignee?: string },
) => apiFetch<ApiIncidentDetail>(`/api/v1/incidents/${id}`, {
  method: 'PATCH',
  body: JSON.stringify(body),
});
