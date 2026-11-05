// Mirrors the backend's ReadinessReport (backend/app/api/health.py).
export interface ComponentStatus {
  status: 'ok' | 'error'
  detail: string | null
}

export interface ReadinessReport {
  status: 'ok' | 'degraded'
  components: Record<string, ComponentStatus>
}

export async function fetchReadiness(signal?: AbortSignal): Promise<ReadinessReport> {
  const res = await fetch('/api/health/ready', { signal })
  // 503 still carries a valid report body; anything else means the API itself is unreachable.
  if (res.status !== 200 && res.status !== 503) {
    throw new Error(`API unreachable (HTTP ${res.status})`)
  }
  return (await res.json()) as ReadinessReport
}

/** Human-readable list of problems, e.g. ["ollama: connection refused"]. Empty when healthy. */
export function describeProblems(report: ReadinessReport): string[] {
  return Object.entries(report.components)
    .filter(([, c]) => c.status === 'error')
    .map(([name, c]) => (c.detail ? `${name}: ${c.detail}` : name))
}
