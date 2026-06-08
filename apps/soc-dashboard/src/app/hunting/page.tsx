import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Search, Filter, Clock, Save, Download, TerminalSquare } from 'lucide-react';

export default function ThreatHunting() {
  const mockResults = [
    { time: '2023-10-24T14:32:01Z', sensor: 'eu-west-1a-ssh', type: 'ssh.login.attempt', src_ip: '192.168.1.105', mitre: 'T1110.001', payload: '{"username": "root", "auth_method": "password"}' },
    { time: '2023-10-24T14:31:45Z', sensor: 'eu-west-1a-ssh', type: 'ssh.login.attempt', src_ip: '192.168.1.105', mitre: 'T1110.001', payload: '{"username": "admin", "auth_method": "password"}' },
    { time: '2023-10-24T14:28:12Z', sensor: 'db-honeypot-01', type: 'postgres.auth.fail', src_ip: '10.0.5.22', mitre: 'T1110.001', payload: '{"user": "postgres", "db": "main"}' },
  ];

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <Search className="text-blue-500" size={32} />
            Threat Hunting
          </h2>
          <p className="text-gray-400 mt-2">Execute KQL queries against historical telemetry and raw logs</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2"><Save size={16}/> Save Query</Button>
          <Button variant="outline" className="gap-2"><Download size={16}/> Export CSV</Button>
        </div>
      </header>

      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-4 space-y-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <TerminalSquare className="absolute left-3 top-3 text-gray-500" size={18} />
              <Input 
                type="text" 
                placeholder="e.g. event_type: ssh.login.attempt AND raw_payload.username: root" 
                className="pl-10 font-mono text-sm bg-gray-950 border-gray-700 text-blue-300"
                defaultValue="event_type: *login* AND src_ip: 192.168.1.*"
              />
            </div>
            <Button className="w-32 bg-blue-600 hover:bg-blue-500">Search</Button>
          </div>
          
          <div className="flex items-center gap-4 flex-wrap">
            <Badge variant="secondary" className="gap-1 px-3 py-1 bg-gray-800 text-gray-300 border-gray-700 cursor-pointer hover:bg-gray-700">
              <Filter size={12} /> Add Filter
            </Badge>
            <div className="h-4 w-px bg-gray-700"></div>
            <Badge variant="outline" className="gap-2 text-gray-400 border-dashed border-gray-700">
              sensor: eu-west-1a-ssh <span className="text-gray-600 hover:text-white cursor-pointer ml-1">×</span>
            </Badge>
            <div className="flex-1"></div>
            <Button variant="ghost" size="sm" className="text-gray-400 gap-2">
              <Clock size={16} /> Last 24 Hours
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="flex-1 bg-gray-900 border-gray-800 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-gray-800 bg-gray-950 flex justify-between items-center">
          <span className="text-sm text-gray-400">Results: <strong className="text-white">{mockResults.length}</strong> hits (0.042s)</span>
          <span className="text-xs text-gray-500 font-mono">Index: tenant-01-telemetry-*</span>
        </div>
        
        <div className="flex-1 overflow-auto p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Sensor</TableHead>
                <TableHead>Event Type</TableHead>
                <TableHead>Source IP</TableHead>
                <TableHead>MITRE</TableHead>
                <TableHead>Raw Payload</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockResults.map((res, i) => (
                <TableRow key={i}>
                  <TableCell className="font-mono text-xs text-gray-400 whitespace-nowrap">{res.time}</TableCell>
                  <TableCell className="font-mono text-xs">{res.sensor}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20">{res.type}</Badge>
                  </TableCell>
                  <TableCell className="font-mono text-xs text-red-400">{res.src_ip}</TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="text-xs">{res.mitre}</Badge>
                  </TableCell>
                  <TableCell className="font-mono text-xs text-gray-500 truncate max-w-md">{res.payload}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
}
