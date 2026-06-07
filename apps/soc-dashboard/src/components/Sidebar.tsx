import Link from 'next/link';

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-gray-300 min-h-screen border-r border-gray-800 flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold text-white tracking-wide">
          <span className="text-blue-500">SENTINELS</span> SOC
        </h1>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        <Link href="/" className="block p-3 rounded-lg hover:bg-gray-800 hover:text-white transition-colors">
          Analyst Dashboard
        </Link>
        <Link href="/mitre" className="block p-3 rounded-lg hover:bg-gray-800 hover:text-white transition-colors">
          MITRE ATT&CK Matrix
        </Link>
        <Link href="/hunting" className="block p-3 rounded-lg hover:bg-gray-800 hover:text-white transition-colors">
          Threat Hunting (OpenSearch)
        </Link>
      </nav>
      <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
        Tenant: <strong>tenant-01</strong><br/>
        Role: L2 Analyst
      </div>
    </aside>
  );
}
