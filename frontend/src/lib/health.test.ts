import { afterEach, describe, expect, it, vi } from 'vitest'

import { describeProblems, fetchReadiness, type ReadinessReport } from './health'

describe('describeProblems', () => {
  it('returns nothing when every component is ok', () => {
    const report: ReadinessReport = {
      status: 'ok',
      components: { postgres: { status: 'ok', detail: null } },
    }
    expect(describeProblems(report)).toEqual([])
  })

  it('lists failing components with their detail', () => {
    const report: ReadinessReport = {
      status: 'degraded',
      components: {
        postgres: { status: 'ok', detail: null },
        ollama: { status: 'error', detail: 'connection refused' },
        qdrant: { status: 'error', detail: null },
      },
    }
    expect(describeProblems(report)).toEqual(['ollama: connection refused', 'qdrant'])
  })
})

describe('fetchReadiness', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('accepts a 503 degraded report as data', async () => {
    const body: ReadinessReport = { status: 'degraded', components: {} }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(body), { status: 503 })))
    await expect(fetchReadiness()).resolves.toEqual(body)
  })

  it('throws when the API itself is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('Bad Gateway', { status: 502 })))
    await expect(fetchReadiness()).rejects.toThrow('API unreachable (HTTP 502)')
  })
})
