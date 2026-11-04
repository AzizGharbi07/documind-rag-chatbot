import { useQuery } from '@tanstack/react-query'

import { describeProblems, fetchReadiness } from './lib/health'

function StatusBadge() {
  const { data, error, isPending } = useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => fetchReadiness(signal),
    refetchInterval: 10_000,
  })

  if (isPending) return <span className="text-sm text-gray-500">Checking services…</span>
  if (error) return <span className="text-sm text-red-600">{error.message}</span>

  const problems = describeProblems(data)
  if (problems.length === 0) return <span className="text-sm text-green-700">All services ready</span>
  return (
    <span className="text-sm text-amber-700" title={problems.join('\n')}>
      Degraded: {problems.join(' · ')}
    </span>
  )
}

export default function App() {
  return (
    <div className="flex h-screen flex-col bg-gray-50 text-gray-900">
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3">
        <h1 className="text-lg font-semibold">DocuMind</h1>
        <StatusBadge />
      </header>
      <main className="flex flex-1 items-center justify-center text-gray-500">
        Upload documents and chat with them. Coming in the next milestones.
      </main>
    </div>
  )
}
