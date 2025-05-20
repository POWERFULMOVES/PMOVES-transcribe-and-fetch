'use client'

import { createClient } from '@/lib/client'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useDropzone } from 'react-dropzone'

// Helper function to generate a random string (for file naming)
const generateRandomString = (length = 10) => {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length))
  }
  return result
}

export const useSupabaseUpload = ({
  bucketName,
  path = '',
  allowedMimeTypes = [],
  maxFiles = 1,
  maxFileSize = 1000 * 1000 * 10, // 10MB default
  onUploadSuccess,
  onUploadError,
}) => {
  const supabase = createClient();
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [successes, setSuccesses] = useState([])
  const [errors, setErrors] = useState([])
  const inputRef = useRef(null)

  const onDrop = useCallback(
    (acceptedFiles, fileRejections) => {
      const newFiles = acceptedFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
          errors: [],
        })
      )

      const rejectedFiles = fileRejections.map(({ file, errors: dropzoneErrors }) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
          errors: dropzoneErrors,
        })
      )

      setFiles((prevFiles) => {
        const allFiles = [...prevFiles, ...newFiles, ...rejectedFiles].slice(0, maxFiles)
        // Clean up old previews
        prevFiles.forEach(file => {
          if (!allFiles.find(f => f.preview === file.preview)) {
            URL.revokeObjectURL(file.preview)
          }
        })
        return allFiles
      })
      setErrors([]) // Clear previous general errors
      setSuccesses([])
    },
    [maxFiles]
  )

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject, open } =
    useDropzone({
      onDrop,
      accept: allowedMimeTypes.length > 0 ? allowedMimeTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}) : undefined,
      maxSize: maxFileSize,
      maxFiles,
      noClick: true, // We'll trigger click via a ref
      noKeyboard: true,
    })

  const handleUpload = async () => {
    if (files.length === 0) return
    setLoading(true)
    setErrors([])
    setSuccesses([])

    const uploadPromises = files
      .filter(file => file.errors.length === 0) // Only upload files without initial validation errors
      .map(async (file) => {
        try {
          const fileExt = file.name.split('.').pop()
          const fileName = `${path ? `${path}/` : ''}${generateRandomString()}-${Date.now()}.${fileExt}`
          const { data, error } = await supabase.storage.from(bucketName).upload(fileName, file)

          if (error) {
            throw error
          }
          if (onUploadSuccess) {
            onUploadSuccess(data, file)
          }
          return { success: true, name: file.name, data }
        } catch (error) {
          if (onUploadError) {
            onUploadError(error, file)
          }
          return { success: false, name: file.name, error }
        }
      })

    const results = await Promise.all(uploadPromises)
    setLoading(false)

    const newSuccesses = results.filter((r) => r.success).map((r) => r.name)
    const newErrors = results
      .filter((r) => !r.success)
      .map((r) => ({ name: r.name, message: r.error.message || 'Upload failed' }))

    setSuccesses(newSuccesses)
    setErrors(newErrors)

    // Update individual file errors for display
    setFiles(prevFiles => prevFiles.map(pf => {
        const uploadError = newErrors.find(ne => ne.name === pf.name);
        if (uploadError) {
            return { ...pf, errors: [...pf.errors, { message: uploadError.message, code: 'upload-failed'}] };
        }
        return pf;
    }));
  }

  useEffect(() => {
    // Revoke the data uris to avoid memory leaks
    return () => files.forEach((file) => URL.revokeObjectURL(file.preview))
  }, [files])

  return {
    files,
    setFiles,
    loading,
    successes,
    errors,
    setErrors, // Expose setErrors for manual error handling if needed
    onUpload: handleUpload,
    getRootProps,
    getInputProps,
    inputRef, // Expose inputRef for DropzoneEmptyState
    open, // Expose open for manual trigger
    isDragActive,
    isDragAccept,
    isDragReject,
    isSuccess: successes.length > 0 && successes.length === files.filter(f => f.errors.length === 0).length && errors.length === 0 && !loading,
    maxFileSize,
    maxFiles,
  }
}