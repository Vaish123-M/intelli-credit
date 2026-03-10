import { useMemo } from 'react'

function prettyJson(value) {
  try {
    return JSON.stringify(value || {}, null, 2)
  } catch {
    return '{}'
  }
}

export default function SchemaMappingEditor({
  schemaMapping,
  onMappingChange,
  onSaveMapping,
  isSaving,
  disabled,
}) {
  const schemaDefinition = useMemo(() => schemaMapping?.schema_definition || [], [schemaMapping])
  const mappingRows = useMemo(() => schemaMapping?.mappings || [], [schemaMapping])
  const structuredOutput = useMemo(() => schemaMapping?.structured_output || {}, [schemaMapping])

  if (!schemaDefinition.length) {
    return null
  }

  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">Dynamic Schema Mapping</h3>
          <p className="mt-1 text-xs text-slate-500">Detected Field {'->'} System Field (editable)</p>
        </div>

        <button
          type="button"
          onClick={onSaveMapping}
          disabled={disabled || isSaving || mappingRows.length === 0}
          className="rounded-lg bg-gradient-to-r from-indigo-600 to-blue-600 px-3 py-2 text-xs font-semibold text-white transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSaving ? 'Saving...' : 'Save Mapping'}
        </button>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-3 py-2 text-left font-semibold text-slate-700">Detected Field</th>
              <th className="px-3 py-2 text-left font-semibold text-slate-700">Value</th>
              <th className="px-3 py-2 text-left font-semibold text-slate-700">System Field</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {mappingRows.length > 0 ? (
              mappingRows.map((row, idx) => (
                <tr key={`${row.detected_field}-${idx}`}>
                  <td className="px-3 py-2 text-slate-800">{row.detected_field || '-'}</td>
                  <td className="px-3 py-2 text-slate-700">{Number(row.value || 0).toLocaleString('en-IN')}</td>
                  <td className="px-3 py-2">
                    <select
                      value={row.system_field || ''}
                      onChange={(event) => onMappingChange(idx, event.target.value)}
                      disabled={disabled}
                      className="w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-800 outline-none ring-blue-100 focus:ring"
                    >
                      {schemaDefinition.map((field) => (
                        <option key={field.key} value={field.label}>
                          {field.label}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="px-3 py-4 text-center text-slate-500">
                  No detected fields available yet. Upload documents to start schema mapping.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 rounded-xl bg-slate-900 p-3 text-xs text-slate-100">
        <p className="mb-2 font-semibold uppercase tracking-[0.08em] text-slate-300">Structured Output JSON</p>
        <pre className="overflow-x-auto whitespace-pre-wrap">{prettyJson(structuredOutput)}</pre>
      </div>
    </section>
  )
}
