import { readdir, stat } from 'node:fs/promises'
import { join } from 'node:path'

const assetsDirectory = join(process.cwd(), 'dist', 'assets')
const maxChunkBytes = 600 * 1024
const entries = await readdir(assetsDirectory)
const oversized = []

for (const entry of entries) {
  if (!entry.endsWith('.js')) continue
  const size = (await stat(join(assetsDirectory, entry))).size
  if (size > maxChunkBytes) {
    oversized.push(`${entry} (${Math.round(size / 1024)} KB)`)
  }
}

if (oversized.length > 0) {
  console.error(`Bundle budget exceeded: ${oversized.join(', ')}`)
  process.exit(1)
}

console.log(`Bundle budget passed: no JavaScript chunk exceeds ${maxChunkBytes / 1024} KB.`)
