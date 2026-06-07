export default function ThreatHunting() {
  return (
    <div className="space-y-6 h-full flex flex-col">
      <header>
        <h2 className="text-3xl font-bold">OpenSearch Threat Hunting</h2>
        <p className="text-gray-400 mt-1">Execute KQL queries against historical telemetry</p>
      </header>

      <div className="bg-gray-900 border border-gray-800 p-4 rounded-xl flex space-x-4">
        <input 
          type="text" 
          placeholder="e.g. event_type: ssh.login.attempt AND raw_payload.username: root" 
          className="flex-1 bg-gray-950 border border-gray-800 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 font-mono text-sm"
        />
        <button className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-medium transition-colors">
          Search
        </button>
      </div>

      <div className="flex-1 bg-gray-900 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        <div className="p-4 border-b border-gray-800 bg-gray-950 flex justify-between">
          <span className="text-sm text-gray-400">Results: 0 hits (0.012s)</span>
          <span className="text-sm text-gray-500 font-mono">Index: tenant-01-telemetry-*</span>
        </div>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-gray-800 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-400">Awaiting search query...</p>
          </div>
        </div>
      </div>
    </div>
  );
}
