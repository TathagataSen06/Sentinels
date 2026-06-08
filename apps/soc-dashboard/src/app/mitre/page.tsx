"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Target, Activity, Shield } from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid 
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

  const getHeatmapColor = (score: number) => {
    if (score === 0) return 'bg-gray-800/50 text-gray-500 border-gray-800';
    if (score < 30) return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
    if (score < 70) return 'bg-orange-500/30 text-orange-200 border-orange-500/50';
    return 'bg-red-500/40 text-red-100 border-red-500/60 font-bold';
  };

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <Target className="text-blue-500" size={32} />
            MITRE ATT&CK Dashboard
          </h2>
          <p className="text-gray-400 mt-2">Real-time mapping of detected threats to the ATT&CK framework</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800">
            <CardTitle className="flex items-center gap-2">
              <Activity size={18} className="text-blue-500"/> Activity Trend (24h)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem', color: '#F3F4F6' }}
                />
                <Line type="monotone" dataKey="events" stroke="#3B82F6" strokeWidth={3} dot={{ r: 4, fill: '#3B82F6' }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800">
            <CardTitle className="flex items-center gap-2">
              <Shield size={18} className="text-blue-500"/> Top Tactics
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tacticCounts} layout="vertical" margin={{ left: 40 }}>
                <XAxis type="number" stroke="#9CA3AF" fontSize={12} />
                <YAxis dataKey="name" type="category" stroke="#9CA3AF" fontSize={11} width={100} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem', color: '#F3F4F6' }}
                  cursor={{ fill: '#374151' }}
                />
                <Bar dataKey="count" fill="#EF4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="flex-1 bg-gray-900 border-gray-800 overflow-hidden flex flex-col">
        <CardHeader className="border-b border-gray-800">
          <CardTitle>Technique Heatmap</CardTitle>
        </CardHeader>
        <CardContent className="p-6 flex-1 overflow-auto">
          <div className="flex gap-4 min-w-max">
            {heatmap.map((col, i) => (
              <div key={i} className="flex-1 min-w-[200px] space-y-2">
                <div className="bg-gray-950 border border-gray-800 p-2 text-center rounded font-semibold text-sm text-gray-300">
                  {col.tactic}
                </div>
                <div className="space-y-2">
                  {col.techniques.map((tech, j) => (
                    <div 
                      key={j} 
                      className={`p-3 rounded text-sm border transition-all ${getHeatmapColor(tech.score)} hover:scale-105 cursor-pointer`}
                      title={`Score: ${tech.score}`}
                    >
                      {tech.name}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
