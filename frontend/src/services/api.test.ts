import { describe, expect, it } from 'vitest'

import { getApiBaseUrl } from './api'

describe('getApiBaseUrl', () => {
  it('falls back to empty baseURL when env is missing', () => {
    expect(getApiBaseUrl({})).toBe('')
  })

  it('trims whitespace', () => {
    expect(getApiBaseUrl({ VITE_API_BASE_URL: '  https://example.com  ' })).toBe('https://example.com')
  })

  it('removes trailing slash', () => {
    expect(getApiBaseUrl({ VITE_API_BASE_URL: 'https://example.com/api/' })).toBe(
      'https://example.com/api',
    )
  })
})
