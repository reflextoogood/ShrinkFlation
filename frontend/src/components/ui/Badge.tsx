import type { DeceptionGapColor, VerificationStatus } from '../../types'

const gapColors: Record<DeceptionGapColor, string> = {
  green:  'bg-green-900/40 text-green-400 border border-green-700',
  yellow: 'bg-yellow-900/40 text-yellow-400 border border-yellow-700',
  red:    'bg-red-900/40 text-red-400 border border-red-700',
}

const gapIcons: Record<DeceptionGapColor, string> = {
  green: '🟢', yellow: '🟡', red: '🔴',
}

export function DeceptionBadge({ color, gap }: { color: DeceptionGapColor; gap: number }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold tabular-nums ${gapColors[color]}`}>
      {gapIcons[color]} +{gap.toFixed(1)} pp
    </span>
  )
}

export function VerifiedBadge({ status }: { status: VerificationStatus }) {
  return status === 'verified' ? (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-900/40 text-blue-400 border border-blue-700">
      ✓ Verified
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-700 text-slate-400">
      ⚠ Unverified
    </span>
  )
}
