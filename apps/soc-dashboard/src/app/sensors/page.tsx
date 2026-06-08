"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Server, Search, Filter, CheckCircle2, XCircle, Puzzle, Building, RefreshCw, Plus } from 'lucide-react';

export default function SensorManagement() {
  const [search, setSearch] = useState('');

  const sensors = [
    { uuid: '128f-49a2-9b2e', name: 'eu-west-1a-ssh', version: 'v2.1.0', tenant: 'Tenant-01', plugins: ['cowrie', 'p0f'], status: 'Active', health: 'Healthy', lastHeartbeat: '12s ago' },
    { uuid: '55a1-8f2e-11bc', name: 'us-east-web', version: 'v2.1.0', tenant: 'Tenant-01', plugins: ['nginx-honey', 'suricata'], status: 'Active', health: 'Healthy', lastHeartbeat: '45s ago' },
    { uuid: '992b-11cc-44df', name: 'db-honeypot-01', version: 'v2.0.4', tenant: 'Tenant-02', plugins: ['postgres-sim', 'mysql-sim'], status: 'Active', health: 'Warning', lastHeartbeat: '2m ago' },
    { uuid: '44fa-22bb-99ee', name: 'edge-router-sim', version: 'v2.1.0', tenant: 'All', plugins: ['cisco-ios'], status: 'Offline', health: 'Critical', lastHeartbeat: '1h 45m ago' },
  ];

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <Server className="text-blue-500" size={32} />
            Sensor Fleet Management
          </h2>
          <p className="text-gray-400 mt-2">Provision, monitor, and manage deception nodes</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2"><RefreshCw size={16}/> Sync</Button>
          <Button className="bg-blue-600 hover:bg-blue-500 gap-2"><Plus size={16}/> Provision Sensor</Button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800 pb-4">
            <CardTitle className="text-sm text-gray-400 font-medium uppercase tracking-wider">Total Sensors</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <span className="text-4xl font-bold">142</span>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800 pb-4">
            <CardTitle className="text-sm text-gray-400 font-medium uppercase tracking-wider">Active</CardTitle>
          </CardHeader>
          <CardContent className="p-6 flex items-center gap-4">
            <span className="text-4xl font-bold text-green-500">138</span>
            <CheckCircle2 className="text-green-500 opacity-20" size={48} />
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800 pb-4">
            <CardTitle className="text-sm text-gray-400 font-medium uppercase tracking-wider">Offline / Error</CardTitle>
          </CardHeader>
          <CardContent className="p-6 flex items-center gap-4">
            <span className="text-4xl font-bold text-red-500">4</span>
            <XCircle className="text-red-500 opacity-20" size={48} />
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800 pb-4">
            <CardTitle className="text-sm text-gray-400 font-medium uppercase tracking-wider">Up to Date (v2.1.0)</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <span className="text-4xl font-bold text-blue-500">124</span>
          </CardContent>
        </Card>
      </div>

      <Card className="flex-1 bg-gray-900 border-gray-800 flex flex-col overflow-hidden">
        <CardHeader className="border-b border-gray-800 bg-gray-950 flex flex-row items-center justify-between pb-3">
          <div className="relative w-72">
            <Search className="absolute left-3 top-2.5 text-gray-500" size={16} />
            <Input 
              placeholder="Search UUID, name, tenant..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-gray-900 border-gray-800 h-9" 
            />
          </div>
          <Button variant="outline" size="sm" className="gap-2 h-9"><Filter size={16}/> Filter</Button>
        </CardHeader>
        <CardContent className="p-0 flex-1 overflow-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>UUID / Hostname</TableHead>
                <TableHead>Tenant</TableHead>
                <TableHead>Version</TableHead>
                <TableHead>Active Plugins</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Heartbeat</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sensors.map((sensor) => (
                <TableRow key={sensor.uuid}>
                  <TableCell>
                    <div className="font-semibold text-gray-200">{sensor.name}</div>
                    <div className="font-mono text-xs text-gray-500">{sensor.uuid}</div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1 text-sm text-gray-400">
                      <Building size={14} /> {sensor.tenant}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={`font-mono text-[10px] ${sensor.version === 'v2.1.0' ? 'text-green-400 border-green-500/30' : 'text-yellow-400 border-yellow-500/30'}`}>
                      {sensor.version}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {sensor.plugins.map(p => (
                        <Badge key={p} variant="secondary" className="text-[10px] px-1.5 py-0 h-5 bg-gray-800 text-gray-300 border-gray-700 flex items-center gap-1">
                          <Puzzle size={10}/> {p}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${sensor.health === 'Healthy' ? 'bg-green-500' : sensor.health === 'Warning' ? 'bg-yellow-500' : 'bg-red-500'}`}></span>
                      <span className="text-sm font-medium">{sensor.status}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-gray-400 font-mono">{sensor.lastHeartbeat}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" className="text-blue-400 hover:text-blue-300">View Telemetry</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
