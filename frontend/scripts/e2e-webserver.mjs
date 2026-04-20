import { spawn } from 'node:child_process'
import { setTimeout as delay } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import { tmpdir } from 'node:os'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const repoRoot = resolve(__dirname, '..', '..')
const backendDir = resolve(repoRoot, 'backend')
const frontendDir = resolve(repoRoot, 'frontend')

function spawnLogged(command, args, options, { exitOnExit = true } = {}) {
  const child = spawn(command, args, { stdio: 'inherit', ...options })
  if (exitOnExit) {
    child.on('exit', (code, signal) => {
      if (signal) process.exit(1)
      process.exit(code ?? 1)
    })
  }
  return child
}

async function waitForHttpOk(url, { timeoutMs = 30_000 } = {}) {
  const start = Date.now()
  while (true) {
    try {
      const res = await fetch(url)
      if (res.ok) return
    } catch {
      // ignore
    }
    if (Date.now() - start > timeoutMs) {
      throw new Error(`Timed out waiting for ${url}`)
    }
    await delay(250)
  }
}

function spawnNpm(args, options, extra) {
  if (process.platform === 'win32') {
    return spawnLogged('cmd.exe', ['/c', 'npm', ...args], options, extra)
  }
  return spawnLogged('npm', args, options, extra)
}

const dbPath = resolve(tmpdir(), `plateaubreaker_e2e_${process.pid}.sqlite3`)

const backend = spawnLogged(
  'python',
  ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
  {
    cwd: backendDir,
    env: {
      ...process.env,
      PLATEAUBREAKER_DB_PATH: dbPath,
    },
  },
)

await waitForHttpOk('http://127.0.0.1:8000/health')

// Build with an explicit API base so the production preview can talk to the backend.
const frontend = spawnNpm(
  ['run', 'build'],
  {
    cwd: frontendDir,
    env: {
      ...process.env,
      VITE_API_BASE_URL: 'http://127.0.0.1:8000',
    },
  },
  { exitOnExit: false },
)

// Wait for build to finish by listening for exit.
await new Promise((resolvePromise, rejectPromise) => {
  frontend.on('exit', (code) => {
    if (code === 0) resolvePromise(undefined)
    else rejectPromise(new Error(`frontend build failed: ${code}`))
  })
})

spawnNpm(
  ['run', 'preview', '--', '--host', '127.0.0.1', '--port', '4173'],
  { cwd: frontendDir, env: process.env },
)

function shutdown() {
  backend.kill()
}

process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)
