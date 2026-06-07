import Link from 'next/link';

export default function Dashboard() {
  const mockIncidents = [
    { id: 'inc-1001', title: 'SSH Brute Force Campaign', severity: 'CRITICAL', status: 'NEW', sensor: 'sensor-8402', time: 'Just now' },
    { id: 'inc-1002', title: 'Suspicious WGET Command', severity: 'HIGH', status: 'INVESTIGATING', sensor: 'sensor-1194', time: '2 mins ago' },
    { id: 'inc-1003', title: 'Failed Login Anomaly', severity: 'MEDIUM', status: 'RESOLVED', sensor: 'sensor-3392', time: '1 hour ago' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">Live Incident Feed</h2>
          <p className="text-gray-400 mt-1">Real-time telemetry streamed via Flink CEP & WebSockets</p>
        </div>
        <div className="flex space-x-4">
          <div className="bg-gray-900 border border-gray-800 px-4 py-2 rounded-lg">
            <span className="text-sm text-gray-500 block">Sensors Online</span>
            <span className="text-xl font-bold text-green-400">98,421</span>
          </div>
          <div className="bg-gray-900 border border-gray-800 px-4 py-2 rounded-lg">
            <span className="text-sm text-gray-500 block">Events / Min</span>
            <span className="text-xl font-bold text-blue-400">1.02M</span>
          </div>
        </div>
      </header>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden shadow-2xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-950 border-b border-gray-800 text-gray-400 text-sm">
              <th className="p-4 font-medium">Incident ID</th>
              <th className="p-4 font-medium">Title</th>
              <th className="p-4 font-medium">Severity</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Sensor</th>
              <th className="p-4 font-medium">Time</th>
              <th className="p-4 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {mockIncidents.map((inc) => (
              <tr key={inc.id} className="hover:bg-gray-800/50 transition-colors">
                <td className="p-4 font-mono text-sm text-gray-400">{inc.id}</td>
                <td className="p-4 font-semibold">{inc.title}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${inc.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400' : inc.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                    {inc.severity}
                  </span>
                </td>
                <td className="p-4 text-sm">{inc.status}</td>
                <td className="p-4 font-mono text-sm">{inc.sensor}</td>
                <td className="p-4 text-sm text-gray-400">{inc.time}</td>
                <td className="p-4">
                  <Link href={`/incidents/${inc.id}`} className="text-blue-400 hover:text-blue-300 text-sm font-medium">
                    Investigate →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
