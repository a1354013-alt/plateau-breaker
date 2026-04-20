import { beforeEach, describe, expect, it, vi } from 'vitest'

import { saveAs } from './analysisDownload'

describe('saveAs', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('creates a download link and revokes the object URL', () => {
    const createObjectUrl = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:weekly-report')
    const revokeObjectUrl = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined)

    const anchor = document.createElement('a')
    const clickSpy = vi.fn()
    anchor.click = clickSpy

    const originalCreateElement = document.createElement.bind(document)
    const createElementSpy = vi.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
      if (tagName === 'a') return anchor
      return originalCreateElement(tagName)
    })

    const appendSpy = vi.spyOn(document.body, 'appendChild')
    const removeSpy = vi.spyOn(document.body, 'removeChild')

    saveAs({ hello: 'world' })

    expect(createObjectUrl).toHaveBeenCalledTimes(1)
    expect(anchor.download).toBe('weekly-report.json')
    expect(clickSpy).toHaveBeenCalledTimes(1)
    expect(appendSpy).toHaveBeenCalledWith(anchor)
    expect(removeSpy).toHaveBeenCalledWith(anchor)
    expect(revokeObjectUrl).toHaveBeenCalledWith('blob:weekly-report')
    expect(createElementSpy).toHaveBeenCalledWith('a')
  })
})
