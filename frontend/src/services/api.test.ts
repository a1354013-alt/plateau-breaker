import { describe, expect, it } from 'vitest'

import { getApiBaseUrl } from './api'

describe('getApiBaseUrl', () => {
  it('falls back to /api when env is missing', () => {
    expect(getApiBaseUrl({})).toBe('/api')
  })

  it('trims whitespace', () => {
    expect(getApiBaseUrl({ VITE_API_BASE_URL: '  /api  ' })).toBe('/api')
  })

  it('removes trailing slash', () => {
    expect(getApiBaseUrl({ VITE_API_BASE_URL: 'https://example.com/api/' })).toBe(
      'https://example.com/api',
    )
  })
})

