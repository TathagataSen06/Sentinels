"use client";

import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Target, Activity, ShieldCheck } from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer,
  CartesianGrid, AreaChart, Area
} from 'recharts';

const trendData = [
  { time: '00:00', events: 120 },
  { time: '04:00', events: 300 },
  { time: '08:00', events: 800 },
  { time: '12:00', events: 450 },
  { time: '16:00', events: 900 },
  { time: '20:00', events: 200 },
];

const coverageData = [
  { name: 'Initial Access', implemented: 14, triggered: 5, gap: 4 },
  { name: 'Execution', implemented: 18, triggered: 8, gap: 2 },
  { name: 'Persistence', implemented: 10, triggered: 2, gap: 8 },
  { name: 'Privilege Escalation', implemented: 12, triggered: 1, gap: 7 },
  { name: 'Defense Evasion', implemented: 24, triggered: 12, gap: 15 },
  { name: 'Credential Access', implemented: 22, triggered: 18, gap: 2 },
];

// Deterministic heatmap data — seeded once, not regenerated on re-render
const tactics = ['Initial Access', 'Execution', 'Persistence', 'Privilege Esc.', 'Defense Evasion', 'Credential Access', 'Discovery'];

function seededRandom(seed: number) {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function generateDeterministicTechniques(tacticIndex: number, count: number) {
  return Array(count).fill(null).map((_, i) => {
    const seed = tacticIndex * 100 + i;
    const id = 100 + Math.floor(seededRandom(seed) * 900);
    const hits = seededRandom(seed + 7) > 0.6 ? Math.floor(seededRandom(seed + 13) * 50) : 0;
    return { name: `T1${id}`, hits };
  });
}

const heatmapMatrix = tactics.map((tactic, i) => ({
  name: tactic,
  techniques: generateDeterministicTechniques(i, 8)
}));

const getColorForHits = (hits: number) => {
  if (hits === 0) return 'bg-gray-800 border-gray-700 text-gray-500';
  if (hits < 10) return 'bg-orange-500/20 border-orange-500/50 text-orange-200';
  if (hits < 30) return 'bg-orange-500/40 border-orange-500 text-white';
  return 'bg-red-600 border-red-500 text-white shadow-[0_0_10px_rgba(220,38,38,0.5)]';
};

export default function MitreDashboard() {
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
                  <linearGradient id="colorEvents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.5rem' }} />
                <Area type="monotone" dataKey="events" stroke="#ef4444" fillOpacity={1} fill="url(#colorEvents)" strokeWidth={2} />
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
                    className={`p-3 border rounded-md text-xs flex justify-between items-center transition-all hover:scale-[1.02] cursor-default ${getColorForHits(tech.hits)}`}
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
