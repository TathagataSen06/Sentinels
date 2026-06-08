import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Activity, ShieldAlert, Users, Clock, AlertTriangle } from 'lucide-react';

export default function Dashboard() {
  const mockIncidents = [
    { id: 'INC-2041', title: 'SSH Brute Force Campaign', severity: 'CRITICAL', status: 'NEW', sensor: 'eu-west-1a-ssh', time: '2 mins ago', assignee: 'Unassigned' },
    { id: 'INC-2040', title: 'Suspicious WGET Command', severity: 'HIGH', status: 'INVESTIGATING', sensor: 'us-east-web', time: '15 mins ago', assignee: 'T. Sen' },
    { id: 'INC-2039', title: 'Failed Login Anomaly', severity: 'MEDIUM', status: 'ESCALATED', sensor: 'db-honeypot-01', time: '1 hour ago', assignee: 'J. Doe' },
    { id: 'INC-2038', title: 'Port Scan Detected', severity: 'LOW', status: 'RESOLVED', sensor: 'edge-router-sim', time: '3 hours ago', assignee: 'Auto-Bot' },
    { id: 'INC-2037', title: 'SMB Enumeration', severity: 'HIGH', status: 'NEW', sensor: 'corp-file-share', time: '4 hours ago', assignee: 'Unassigned' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <ShieldAlert className="text-blue-500" size={32} />
            Live Incident Feed
          </h2>
          <p className="text-gray-400 mt-2">Real-time telemetry and threat intelligence correlation</p>
        </div>
        <div className="flex gap-4">
          <Card className="bg-gray-900 border-gray-800">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-blue-500/10 rounded-lg">
                <Activity className="text-blue-500" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Events / Min</p>
                <p className="text-2xl font-bold text-white">1.24M</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-gray-900 border-gray-800">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-red-500/10 rounded-lg">
                <AlertTriangle className="text-red-500" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Active Criticals</p>
                <p className="text-2xl font-bold text-white">3</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </header>

      <Card className="bg-gray-900 border-gray-800">
        <CardHeader className="border-b border-gray-800">
          <CardTitle>Recent Detections</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Incident ID</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Assignee</TableHead>
                <TableHead>Sensor</TableHead>
                <TableHead>Time</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockIncidents.map((inc) => (
                <TableRow key={inc.id}>
                  <TableCell className="font-mono text-xs text-gray-400">{inc.id}</TableCell>
                  <TableCell className="font-medium">{inc.title}</TableCell>
                  <TableCell>
                    <Badge variant={
                      inc.severity === 'CRITICAL' ? 'destructive' :
                      inc.severity === 'HIGH' ? 'warning' :
                      inc.severity === 'MEDIUM' ? 'default' : 'secondary'
                    }>
                      {inc.severity}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-xs uppercase tracking-wider font-semibold text-gray-400">
                      {inc.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Users size={14} className="text-gray-500" />
                      <span className="text-sm text-gray-300">{inc.assignee}</span>
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-xs text-gray-400">{inc.sensor}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2 text-gray-400">
                      <Clock size={14} />
                      <span className="text-sm">{inc.time}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <Link 
                      href={`/incidents/${inc.id}`} 
                      className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background hover:bg-gray-800 hover:text-gray-100 h-9 px-4 py-2 border border-gray-700 bg-transparent text-gray-200"
                    >
                      Investigate
                    </Link>
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
