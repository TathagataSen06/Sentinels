"use client";

import { useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ShieldAlert, Activity, AlertTriangle, Target, Globe } from 'lucide-react';
import { useSocketStore } from '@/lib/store/useSocketStore';
import { 
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer,
} from 'recharts';

const trendData = [
  { time: '00:00', incidents: 12 }, { time: '04:00', incidents: 30 },
  { time: '08:00', incidents: 80 }, { time: '12:00', incidents: 45 },
  { time: '16:00', incidents: 90 }, { time: '20:00', incidents: 20 },
];

const eventTypes = ['SSH Login Attempt', 'HTTP Reconnaissance', 'Canary Credential Access', 'Incident Created'] as const;
const sensors = ['eu-west-1a-ssh', 'us-east-web', 'corp-file-share', 'db-honeypot'] as const;
const severities = ['INFO', 'WARNING', 'CRITICAL'] as const;

export default function GlobalDashboard() {
  const { events, connect, disconnect, addEvent } = useSocketStore();

  const simulateEvent = useCallback(() => {
    addEvent({
      type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
      message: `Detected anomalous behavior from ${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      sensor: sensors[Math.floor(Math.random() * sensors.length)],
      severity: severities[Math.floor(Math.random() * severities.length)],
    });
  }, [addEvent]);

  useEffect(() => {
    connect();
    const interval = setInterval(simulateEvent, 3000);
    return () => {
      clearInterval(interval);
      disconnect();
    };
  }, [connect, disconnect, simulateEvent]);

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header>
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <Activity className="text-blue-500" size={32} />
          SOC Global Dashboard
        </h2>
        <p className="text-gray-400 mt-2">Real-time enterprise threat landscape overview</p>
      </header>

      {/* Security KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-red-500/10 rounded-lg"><AlertTriangle className="text-red-500" /></div>
            <div><p className="text-sm text-gray-500">Active Incidents</p><p className="text-2xl font-bold text-white">24</p></div>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-orange-500/10 rounded-lg"><ShieldAlert className="text-orange-500" /></div>
            <div><p className="text-sm text-gray-500">Critical / High</p><p className="text-2xl font-bold text-white">8</p></div>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg"><Activity className="text-blue-500" /></div>
            <div><p className="text-sm text-gray-500">Events / Min</p><p className="text-2xl font-bold text-white">1.24M</p></div>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-green-500/10 rounded-lg"><Globe className="text-green-500" /></div>
            <div><p className="text-sm text-gray-500">Active Sensors</p><p className="text-2xl font-bold text-white">138</p></div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Attack Overview Charts */}
        <div className="lg:col-span-2 space-y-6 flex flex-col">
          <Card className="bg-gray-900 border-gray-800 flex-1">
            <CardHeader className="border-b border-gray-800 pb-4">
              <CardTitle className="text-sm text-gray-400 font-medium uppercase tracking-wider flex items-center gap-2">
                <Target size={16}/> Incident Trend (24h)
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="time" stroke="#9CA3AF" fontSize={12} />
                  <YAxis stroke="#9CA3AF" fontSize={12} />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem', color: '#F3F4F6' }} />
                  <Line type="monotone" dataKey="incidents" stroke="#EF4444" strokeWidth={3} dot={{ r: 4, fill: '#EF4444' }} activeDot={{ r: 6, stroke: '#EF4444', strokeWidth: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Real-Time Activity Feed */}
        <Card className="bg-gray-900 border-gray-800 flex flex-col overflow-hidden min-h-0">
          <CardHeader className="border-b border-gray-800 pb-4 bg-gray-950 flex flex-row items-center justify-between shrink-0">
            <CardTitle className="text-sm text-gray-400 font-medium uppercase tracking-wider flex items-center gap-2">
              <Activity size={16} className="text-green-500 animate-pulse"/> Live Activity Stream
            </CardTitle>
            <Badge variant="outline" className="text-xs bg-green-500/10 text-green-400 border-green-500/20">Connected</Badge>
          </CardHeader>
          <CardContent className="p-0 flex-1 overflow-y-auto min-h-0">
            <div className="divide-y divide-gray-800">
              {events.length === 0 ? (
                <div className="p-8 text-center text-gray-500 text-sm">Listening for events...</div>
              ) : (
                events.map((event) => (
                  <div key={event.id} className="p-4 hover:bg-gray-800/50 transition-colors">
                    <div className="flex justify-between items-start mb-1">
                      <span className={`text-sm font-semibold ${event.severity === 'CRITICAL' ? 'text-red-400' : event.severity === 'WARNING' ? 'text-yellow-400' : 'text-blue-400'}`}>
                        {event.type}
                      </span>
                      <span className="text-xs text-gray-500 font-mono shrink-0 ml-2">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300 mb-2">{event.message}</p>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-[10px] px-1.5 py-0 h-4 bg-gray-800 text-gray-400 border-gray-700">
                        {event.sensor}
                      </Badge>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
