import { spawn } from 'node:child_process'
import { mkdir, rm, cp } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { chromium } from 'playwright'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const repoRoot = path.resolve(__dirname, '..', '..')
const frontendDist = path.join(repoRoot, 'frontend', 'dist')
const backendStaticDist = path.join(repoRoot, 'backend', 'app', 'static', 'dist')
const screenshotsDir = path.join(repoRoot, 'docs', 'screenshots')

const backendUrl = 'http://127.0.0.1:8000'

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function waitForHealth() {
  const deadline = Date.now() + 30_000
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`${backendUrl}/health`)
      if (res.ok) return
    } catch {
      // ignore
    }
    await sleep(250)
  }
  throw new Error('Timed out waiting for backend /health')
}

function startBackend() {
  const python = process.env.PYTHON ?? 'python'
  const dbPath = path.join(os.tmpdir(), 'plateaubreaker_screenshots.sqlite3')

  const env = {
    ...process.env,
    APP_TIMEZONE: process.env.APP_TIMEZONE ?? 'Asia/Taipei',
    PLATEAUBREAKER_DB_PATH: process.env.PLATEAUBREAKER_DB_PATH ?? dbPath,
  }

  // Best-effort: start from a clean DB so screenshots are deterministic.
  rm(env.PLATEAUBREAKER_DB_PATH, { force: true }).catch(() => {})

  const proc = spawn(
    python,
    [
      '-m',
      'uvicorn',
      'app.main:app',
      '--app-dir',
      'backend',
      '--host',
      '127.0.0.1',
      '--port',
      '8000',
    ],
    { cwd: repoRoot, env, stdio: 'pipe' },
  )

  proc.stdout.on('data', (d) => process.stdout.write(d))
  proc.stderr.on('data', (d) => process.stderr.write(d))

  return proc
}

async function seedRecords() {
  const today = new Date()
  const anchor = new Date(today.getTime() - 24 * 60 * 60 * 1000) // safe past day

  for (let i = 7; i >= 0; i -= 1) {
    const d = new Date(anchor.getTime() - i * 24 * 60 * 60 * 1000)
    const recordDate = d.toISOString().slice(0, 10)
    const res = await fetch(`${backendUrl}/api/health-records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_date: recordDate,
        weight: 75.0 - (7 - i) * 0.1,
        sleep_hours: 7.0,
        calories: 2000,
        protein: 120,
        exercise_minutes: 30,
        exercise_type: 'Walking',
        steps: 8000,
        note: null,
      }),
    })
    // Ignore conflicts in case the DB wasn't fully cleaned.
    if (!res.ok && res.status !== 409) {
      throw new Error(`Seed failed: ${res.status} ${await res.text()}`)
    }
  }
}

async function main() {
  await mkdir(screenshotsDir, { recursive: true })
  await rm(backendStaticDist, { recursive: true, force: true })
  await mkdir(path.dirname(backendStaticDist), { recursive: true })
  await cp(frontendDist, backendStaticDist, { recursive: true })

  const backendProc = startBackend()

  try {
    await waitForHealth()
    await seedRecords()

    const browser = await chromium.launch()
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })

    await page.goto(`${backendUrl}/`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(300)
    await page.screenshot({ path: path.join(screenshotsDir, 'dashboard.png'), fullPage: true })

    await page.goto(`${backendUrl}/records`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(300)
    await page.screenshot({ path: path.join(screenshotsDir, 'records.png'), fullPage: true })

    await page.goto(`${backendUrl}/analysis`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(300)
    await page.screenshot({ path: path.join(screenshotsDir, 'analysis.png'), fullPage: true })

    await browser.close()
  } finally {
    backendProc.kill('SIGTERM')
    await sleep(500)
    await rm(backendStaticDist, { recursive: true, force: true })
  }
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
