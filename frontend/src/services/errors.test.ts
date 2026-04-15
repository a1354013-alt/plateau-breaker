import { describe, expect, it } from 'vitest'

import { getApiErrorMessage } from './errors'

describe('getApiErrorMessage', () => {
  it('prefers string detail from API response', () => {
    const err = {
      isAxiosError: true,
      message: 'Request failed',
      response: { data: { detail: 'Bad input' } },
    }

    expect(getApiErrorMessage(err, 'fallback')).toBe('Bad input')
  })

  it('falls back to axios error message when detail is missing/blank', () => {
    const err = {
      isAxiosError: true,
      message: 'Network error',
      response: { data: { detail: '   ' } },
    }

    expect(getApiErrorMessage(err, 'fallback')).toBe('Network error')
  })

  it('handles non-axios errors', () => {
    expect(getApiErrorMessage(new Error('boom'), 'fallback')).toBe('boom')
    expect(getApiErrorMessage('not-an-error', 'fallback')).toBe('fallback')
  })
})

