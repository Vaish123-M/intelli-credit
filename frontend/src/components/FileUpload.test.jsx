import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

vi.mock('react-dropzone', () => ({
  useDropzone: ({ onDrop }) => ({
    getRootProps: () => ({ onClick: () => onDrop([new File(['data'], 'annual.csv', { type: 'text/csv' })]) }),
    getInputProps: () => ({ onChange: () => {} }),
    isDragActive: false,
    fileRejections: [],
  }),
}))

import FileUpload from './FileUpload'

const requiredDocTypes = [
  'ALM (Asset Liability Management)',
  'Shareholding Pattern',
  'Borrowing Profile',
  'Annual Report',
  'Portfolio Cuts / Performance Data',
]

const classifications = requiredDocTypes.map((detected_type, index) => ({
  file_name: `document-${index}.csv`,
  detected_type,
  confidence: 0.95,
  approved: true,
}))

function renderUpload(overrides = {}) {
  return render(
    <FileUpload
      files={[]}
      onFilesSelected={vi.fn()}
      onUpload={vi.fn()}
      onClassify={vi.fn()}
      classifications={[]}
      onClassificationChange={vi.fn()}
      onClassificationApproval={vi.fn()}
      isUploading={false}
      isProcessing={false}
      isClassifying={false}
      requiredDocTypes={requiredDocTypes}
      {...overrides}
    />
  )
}

describe('FileUpload', () => {
  it('disables actions until files are selected', () => {
    renderUpload()

    expect(screen.getByRole('button', { name: 'Classify Documents' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Upload and Analyze' })).toBeDisabled()
  })

  it('reports missing required document types', () => {
    renderUpload({
      files: [new File(['data'], 'annual.csv', { type: 'text/csv' })],
      classifications: [classifications[0]],
    })

    expect(screen.getByText(/Missing required types:/i)).toBeInTheDocument()
    expect(screen.getByText(/Approve classifications and include all 5 required document types/i)).toBeInTheDocument()
  })

  it('enables upload when all classifications are approved', () => {
    renderUpload({
      files: classifications.map((item) => new File(['data'], item.file_name, { type: 'text/csv' })),
      classifications,
    })

    expect(screen.getByText('All required document categories are covered.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Upload and Analyze' })).toBeEnabled()
  })
})
