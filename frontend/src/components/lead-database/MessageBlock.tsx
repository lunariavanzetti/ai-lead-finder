import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'

function legacyCopy(text: string): boolean {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.focus()
  textarea.select()
  let ok = false
  try {
    ok = document.execCommand('copy')
  } catch {
    ok = false
  }
  document.body.removeChild(textarea)
  return ok
}

export function MessageBlock({ title, message }: { title: string; message: string }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    let success = false
    try {
      await navigator.clipboard.writeText(message)
      success = true
    } catch {
      success = legacyCopy(message)
    }

    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } else {
      toast.error('Could not copy — your browser blocked clipboard access. Select the text and copy it manually.')
    }
  }

  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <h4 className="text-sm font-semibold">{title}</h4>
        <Button size="sm" variant="ghost" className="h-7 px-2 text-xs" onClick={handleCopy}>
          {copied ? <Check className="h-3.5 w-3.5 text-success" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? 'Copied' : 'Copy'}
        </Button>
      </div>
      <p className="rounded-md bg-muted/50 p-3 text-sm leading-relaxed select-text">{message}</p>
    </div>
  )
}
