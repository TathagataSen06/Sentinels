export default function IncidentWorkspace({ params }: { params: { id: string } }) {
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-start border-b border-gray-800 pb-6">
        <div>
          <h2 className="text-3xl font-bold">Incident Workspace: {params.id}</h2>
          <p className="text-red-400 font-medium mt-1">Status: CRITICAL • Unassigned</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-medium transition-colors">
          Assign to Me
        </button>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Attack Timeline View */}
        <div className="col-span-2 space-y-4">
          <h3 className="text-xl font-semibold">Attack Timeline</h3>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 relative">
            <div className="absolute left-8 top-10 bottom-10 w-0.5 bg-gray-800"></div>
            
            <div className="space-y-8 relative z-10">
              <div className="flex gap-4">
                <div className="w-4 h-4 rounded-full bg-blue-500 mt-1 ring-4 ring-gray-900"></div>
                <div>
                  <p className="text-sm text-gray-400">10:45:02 UTC</p>
                  <p className="font-medium">Initial Connection established on Port 22 (SSH)</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-4 h-4 rounded-full bg-yellow-500 mt-1 ring-4 ring-gray-900"></div>
                <div>
                  <p className="text-sm text-gray-400">10:45:03 UTC</p>
                  <p className="font-medium">Threat Intel Match</p>
                  <p className="text-sm text-gray-400 bg-gray-800 p-2 rounded mt-1 inline-block">Redis Cache Hit: 192.168.1.100 (AbuseIPDB Confidence: 100%)</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-4 h-4 rounded-full bg-red-500 mt-1 ring-4 ring-gray-900 shadow-[0_0_15px_rgba(239,68,68,0.5)]"></div>
                <div>
                  <p className="text-sm text-gray-400">10:45:05 UTC</p>
                  <p className="font-medium">Incident Triggered: Sigma Rule Match</p>
                  <p className="text-sm text-red-300 bg-red-950/30 border border-red-900 p-2 rounded mt-1">Rule: Suspicious SSH Login. Tactic: Credential Access.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Notes & Evidence */}
        <div className="space-y-4">
          <h3 className="text-xl font-semibold">Evidence & Actions</h3>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
            <div>
              <label className="text-sm text-gray-400 block mb-2">Analyst Notes</label>
              <textarea 
                className="w-full bg-gray-950 border border-gray-800 rounded p-3 text-sm focus:outline-none focus:border-blue-500 text-white min-h-[100px]"
                placeholder="Begin investigation..."
              ></textarea>
            </div>
            <button className="w-full bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded font-medium transition-colors">
              Isolate Sensor
            </button>
            <button className="w-full bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded font-medium transition-colors">
              Add IP to Global Blocklist
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
