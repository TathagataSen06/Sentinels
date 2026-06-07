export default function MitreDashboard() {
  const tactics = [
    { name: 'Initial Access', score: 85, color: 'bg-red-500' },
    { name: 'Execution', score: 40, color: 'bg-yellow-500' },
    { name: 'Persistence', score: 10, color: 'bg-green-500' },
    { name: 'Privilege Escalation', score: 25, color: 'bg-green-400' },
    { name: 'Defense Evasion', score: 60, color: 'bg-orange-500' },
    { name: 'Credential Access', score: 95, color: 'bg-red-600' },
    { name: 'Discovery', score: 70, color: 'bg-orange-400' },
    { name: 'Lateral Movement', score: 15, color: 'bg-green-500' },
  ];

  return (
    <div className="space-y-8">
      <header>
        <h2 className="text-3xl font-bold">MITRE ATT&CK Heatmap</h2>
        <p className="text-gray-400 mt-1">Real-time threat landscape based on Flink aggregations</p>
      </header>

      <div className="grid grid-cols-4 gap-4">
        {tactics.map((t) => (
          <div key={t.name} className="bg-gray-900 border border-gray-800 p-4 rounded-xl hover:border-gray-700 transition-colors cursor-pointer group">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-medium text-gray-200 group-hover:text-white transition-colors">{t.name}</h3>
              <span className="text-xs font-mono text-gray-500">{t.score}%</span>
            </div>
            <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden">
              <div className={`h-full ${t.color}`} style={{ width: `${t.score}%` }}></div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-xl font-semibold mb-4">Top Observed Techniques</h3>
        <ul className="space-y-3">
          <li className="flex justify-between items-center border-b border-gray-800 pb-2">
            <span>T1110.001 - Password Guessing</span>
            <span className="text-red-400 font-mono">14,231 hits</span>
          </li>
          <li className="flex justify-between items-center border-b border-gray-800 pb-2">
            <span>T1059.004 - Unix Shell</span>
            <span className="text-orange-400 font-mono">3,102 hits</span>
          </li>
          <li className="flex justify-between items-center border-b border-gray-800 pb-2">
            <span>T1082 - System Information Discovery</span>
            <span className="text-yellow-400 font-mono">941 hits</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
