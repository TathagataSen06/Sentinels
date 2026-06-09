"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Target, Activity, Shield, ShieldCheck } from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, AreaChart, Area
} from 'recharts';

export default function MitreDashboard() {
  const trendData = [
    { time: '00:00', events: 120 },
    { time: '04:00', events: 300 },
    { time: '08:00', events: 800 },
    { time: '12:00', events: 450 },
    { time: '16:00', events: 900 },
    { time: '20:00', events: 200 },
  ];

  const tacticCounts = [
    { name: 'Initial Access', count: 45 },
    { name: 'Execution', count: 30 },
    { name: 'Persistence', count: 12 },
    { name: 'Privilege Escalation', count: 8 },
    { name: 'Defense Evasion', count: 25 },
    { name: 'Credential Access', count: 89 },
    { name: 'Discovery', count: 60 },
  ];

  const heatmap = [
    {
      tactic: "Initial Access",
      techniques: [
        { name: "Drive-by Compromise", score: 0 },
        { name: "Exploit Public-Facing App", score: 80 },
        { name: "Phishing", score: 20 },
        { name: "Valid Accounts", score: 95 },
      ]
    },
    {
      tactic: "Execution",
      techniques: [
        { name: "Command and Scripting", score: 60 },
        { name: "Scheduled Task/Job", score: 10 },
        { name: "System Services", score: 5 },
        { name: "WMI", score: 0 },
      ]
    },
    {
      tactic: "Credential Access",
      techniques: [
        { name: "Brute Force", score: 100 },
        { name: "Credentials from Password Stores", score: 30 },
        { name: "OS Credential Dumping", score: 10 },
        { name: "Steal Web Session Cookie", score: 0 },
      ]
    },
    {
      tactic: "Discovery",
      techniques: [
        { name: "Account Discovery", score: 40 },
        { name: "Network Service Scanning", score: 90 },
        { name: "Process Discovery", score: 20 },
        { name: "System Information Discovery", score: 70 },
      ]
    }
  ];

  const coverageData = [
    { name: 'Initial Access', implemented: 14, triggered: 5, gap: 4 },
    { name: 'Execution', implemented: 18, triggered: 8, gap: 2 },
    { name: 'Persistence', implemented: 10, triggered: 2, gap: 8 },
    { name: 'Privilege Escalation', implemented: 12, triggered: 1, gap: 7 },
    { name: 'Defense Evasion', implemented: 24, triggered: 12, gap: 15 },
    { name: 'Credential Access', implemented: 22, triggered: 18, gap: 2 },
  ];

  // Mock heatmap matrix
  const tactics = ['Initial Access', 'Execution', 'Persistence', 'Privilege Esc.', 'Defense Evasion', 'Credential Access', 'Discovery'];
  const generateTechniques = (tactic: string, count: number) => {
    return Array(count).fill(null).map((_, i) => ({
      name: `T1${Math.floor(Math.random() * 900) + 100}`,
      hits: Math.floor(Math.random() * 100) > 60 ? Math.floor(Math.random() * 50) : 0
    }));
  };

  const heatmapMatrix = tactics.map(tactic => ({
    name: tactic,
    techniques: generateTechniques(tactic, 8)
  }));

  const getColorForHits = (hits: number) => {
    if (hits === 0) return 'bg-gray-800 border-gray-700 text-gray-500';
    if (hits < 10) return 'bg-orange-500/20 border-orange-500/50 text-orange-200';
    if (hits < 30) return 'bg-orange-500/40 border-orange-500 text-white';
    return 'bg-red-600 border-red-500 text-white shadow-[0_0_10px_rgba(220,38,38,0.5)]';
  };

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header>
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <Target className="text-blue-500" size={32} />
          MITRE ATT&CK Dashboard
        </h2>
        <p className="text-gray-400 mt-2">Map adversary behavior to the ATT&CK framework</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800 pb-4">
            <CardTitle className="text-sm text-gray-400 font-medium uppercase tracking-wider flex items-center gap-2">
              <Activity size={16}/> ATT&CK Trend (24h)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorIA" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorCA" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.5rem' }} />
                <Area type="monotone" dataKey="Initial Access" stroke="#ef4444" fillOpacity={1} fill="url(#colorIA)" />
                <Area type="monotone" dataKey="Credential Access" stroke="#f59e0b" fillOpacity={1} fill="url(#colorCA)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800 pb-4">
            <CardTitle className="text-sm text-gray-400 font-medium uppercase tracking-wider flex items-center gap-2">
              <ShieldCheck size={16}/> Detection Coverage
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={coverageData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
                <XAxis type="number" stroke="#9ca3af" fontSize={12} />
                <YAxis dataKey="name" type="category" stroke="#9ca3af" fontSize={12} width={100} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.5rem' }} />
                <Bar dataKey="implemented" stackId="a" fill="#3b82f6" name="Implemented" />
                <Bar dataKey="triggered" stackId="a" fill="#ef4444" name="Triggered (24h)" />
                <Bar dataKey="gap" stackId="a" fill="#374151" name="Coverage Gap" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-gray-900 border-gray-800 flex-1 flex flex-col">
        <CardHeader className="border-b border-gray-800">
          <CardTitle className="flex justify-between items-center">
            <span>Technique Heatmap</span>
            <div className="flex items-center gap-3 text-xs font-normal">
              <span className="flex items-center gap-1"><span className="w-3 h-3 bg-gray-800 border border-gray-700 rounded-sm"></span> No Data</span>
              <span className="flex items-center gap-1"><span className="w-3 h-3 bg-orange-500/40 border border-orange-500 rounded-sm"></span> Active</span>
              <span className="flex items-center gap-1"><span className="w-3 h-3 bg-red-600 border border-red-500 rounded-sm"></span> High Frequency</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 overflow-x-auto">
          <div className="flex min-w-max gap-4">
            {heatmapMatrix.map((col, i) => (
              <div key={i} className="flex-1 w-48 flex flex-col gap-2">
                <div className="bg-gray-800 p-2 text-center rounded-md border border-gray-700 font-semibold text-sm text-gray-200 mb-2 truncate">
                  {col.name}
                </div>
                {col.techniques.map((tech, j) => (
                  <div 
                    key={j} 
                    className={`p-3 border rounded-md text-xs flex justify-between items-center transition-all ${getColorForHits(tech.hits)}`}
                  >
                    <span className="font-mono">{tech.name}</span>
                    {tech.hits > 0 && <Badge variant="secondary" className="bg-black/30 border-none text-[10px] px-1 py-0">{tech.hits}</Badge>}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
