import { useMemo, useState } from 'react'

export default function SchemaMappingEditor({
  schemaMapping,
  onMappingChange,
  onSchemaDefinitionChange,
  onSaveMapping,
  isSaving,
  disabled,
}) {
  const schemaDefinition = useMemo(() => schemaMapping?.schema_definition || [], [schemaMapping])
  const mappingRows = useMemo(() => schemaMapping?.mappings || [], [schemaMapping])
  const [newFieldLabel, setNewFieldLabel] = useState('')

  if (!schemaDefinition.length) {
    return null
  }

  const handleAddField = () => {
    const label = newFieldLabel.trim()
    if (!label) return

    const keyBase = label
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '') || 'field'

    const existingKeys = new Set(schemaDefinition.map((field) => field.key))
    let nextKey = keyBase
    let suffix = 2
    while (existingKeys.has(nextKey)) {
      nextKey = `${keyBase}_${suffix}`
      suffix += 1
    }

    onSchemaDefinitionChange?.([...schemaDefinition, { key: nextKey, label }])
    setNewFieldLabel('')
  }

  const handleRemoveField = (keyToRemove) => {
    if (schemaDefinition.length <= 1) return
    onSchemaDefinitionChange?.(schemaDefinition.filter((field) => field.key !== keyToRemove))
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
          className="rounded-lg bg-linear-to-r from-indigo-600 to-blue-600 px-3 py-2 text-xs font-semibold text-white transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSaving ? 'Saving...' : 'Save Mapping'}
        </button>
      </div>

      <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p className="text-xs font-bold uppercase tracking-widest text-slate-600">Schema Definition</p>
        <p className="mt-1 text-xs text-slate-500">Add or remove output fields used for extracted structured data.</p>

        <div className="mt-3 flex flex-wrap gap-2">
          <input
            type="text"
            value={newFieldLabel}
            onChange={(event) => setNewFieldLabel(event.target.value)}
            disabled={disabled}
            placeholder="Add field label (for example: DSCR)"
            className="min-w-55 flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none ring-blue-100 focus:ring"
          />
          <button
            type="button"
            onClick={handleAddField}
            disabled={disabled || !newFieldLabel.trim()}
            className="rounded-lg border border-blue-300 bg-blue-50 px-3 py-2 text-xs font-semibold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Add Field
          </button>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {schemaDefinition.map((field) => (
            <div key={field.key} className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700">
              <span>{field.label}</span>
              <button
                type="button"
                onClick={() => handleRemoveField(field.key)}
                disabled={disabled || schemaDefinition.length <= 1}
                className="rounded px-1 text-rose-600 hover:bg-rose-50 disabled:cursor-not-allowed disabled:opacity-50"
                aria-label={`Remove ${field.label}`}
              >
                x
              </button>
            </div>
          ))}
        </div>
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

    </section>
  )
}
