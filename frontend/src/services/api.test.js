import { describe, expect, it, vi } from 'vitest'

import { onboardEntity } from './api'

describe('API client', () => {
  it('returns successful JSON payloads', async () => {
    const payload = { entity_id: 'ent_123' }
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(payload), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )

    await expect(onboardEntity({ company_name: 'Acme' })).resolves.toEqual(payload)
    expect(globalThis.fetch).toHaveBeenCalled()
  })

  it('surfaces API detail errors', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Invalid company data' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    )

    await expect(onboardEntity({ company_name: '' })).rejects.toThrow('Invalid company data')
  })
})
