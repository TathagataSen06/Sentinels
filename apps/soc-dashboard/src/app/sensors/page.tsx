import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Server, Plus, RefreshCw, Power, CheckCircle2, XCircle } from 'lucide-react';

export default function SensorManagement() {
  const sensors = [
    { id: 'sensor-8402', name: 'eu-west-1a-ssh', type: 'SSH Honeypot', status: 'Active', health: 'Healthy', lastHeartbeat: '12s ago', ip: '10.0.1.20' },
    { id: 'sensor-1194', name: 'us-east-web', type: 'HTTP Proxy', status: 'Active', health: 'Healthy', lastHeartbeat: '45s ago', ip: '10.0.5.55' },
    { id: 'sensor-3392', name: 'db-honeypot-01', type: 'PostgreSQL', status: 'Active', health: 'Warning', lastHeartbeat: '2m ago', ip: '10.0.10.15' },
    { id: 'sensor-9912', name: 'edge-router-sim', type: 'Router Sim', status: 'Offline', health: 'Critical', lastHeartbeat: '1h 45m ago', ip: '192.168.1.1' },
    { id: 'sensor-4455', name: 'corp-file-share', type: 'SMB Shares', status: 'Pending', health: 'Unknown', lastHeartbeat: 'Never', ip: '10.0.2.100' },
  ];

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <Server className="text-blue-500" size={32} />
            Sensor Management
          </h2>
          <p className="text-gray-400 mt-2">Provision, monitor, and manage deception nodes</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2"><RefreshCw size={16}/> Sync</Button>
          <Button className="bg-blue-600 hover:bg-blue-500 gap-2"><Plus size={16}/> Provision Sensor</Button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
      </div>

      <Card className="flex-1 bg-gray-900 border-gray-800 flex flex-col overflow-hidden">
        <CardHeader className="border-b border-gray-800">
          <CardTitle>Sensor Inventory</CardTitle>
        </CardHeader>
        <CardContent className="p-0 flex-1 overflow-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Sensor ID</TableHead>
                <TableHead>Hostname</TableHead>
                <TableHead>Profile</TableHead>
                <TableHead>IP Address</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Health</TableHead>
                <TableHead>Last Heartbeat</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sensors.map((sensor) => (
                <TableRow key={sensor.id}>
                  <TableCell className="font-mono text-xs text-gray-400">{sensor.id}</TableCell>
                  <TableCell className="font-semibold">{sensor.name}</TableCell>
                  <TableCell className="text-gray-300">{sensor.type}</TableCell>
                  <TableCell className="font-mono text-xs text-gray-400">{sensor.ip}</TableCell>
                  <TableCell>
                    <Badge variant={
                      sensor.status === 'Active' ? 'success' :
                      sensor.status === 'Offline' ? 'destructive' : 'secondary'
                    }>
                      {sensor.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className={`text-sm flex items-center gap-2 ${
                      sensor.health === 'Healthy' ? 'text-green-400' :
                      sensor.health === 'Warning' ? 'text-yellow-400' :
                      sensor.health === 'Critical' ? 'text-red-400' : 'text-gray-500'
                    }`}>
                      <span className="w-2 h-2 rounded-full bg-current"></span>
                      {sensor.health}
                    </span>
                  </TableCell>
                  <TableCell className="text-sm text-gray-400">{sensor.lastHeartbeat}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" className="text-blue-400 hover:text-blue-300">
                      Configure
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300 ml-2">
                      <Power size={14} />
                    </Button>
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
