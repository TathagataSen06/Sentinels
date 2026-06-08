"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Globe, ShieldAlert, ShieldCheck, Search, Database } from 'lucide-react';

export default function ThreatIntel() {
  const [search, setSearch] = useState('185.150.11.20');

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <Globe className="text-blue-500" size={32} />
            Threat Intelligence Center
          </h2>
          <p className="text-gray-400 mt-2">Enrich indicators and track adversary infrastructure</p>
        </div>
      </header>

      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-4 flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-gray-500" size={18} />
            <Input 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 font-mono text-sm bg-gray-950 border-gray-800"
              placeholder="Search IP, Domain, Hash..."
            />
          </div>
          <Button className="bg-blue-600 hover:bg-blue-500 px-8">Enrich Indicator</Button>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800">
            <CardTitle className="text-lg flex items-center gap-2">
              <Database size={18} /> AbuseIPDB
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Reputation Score</span>
              <Badge variant="destructive" className="bg-red-500/20 text-red-500">100% (Malicious)</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Total Reports</span>
              <span className="font-mono text-white">1,402</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Country</span>
              <span className="text-white">RU (Russia)</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">ISP / ASN</span>
              <span className="font-mono text-white text-right">AS12345<br/>Example Hosting</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800">
            <CardTitle className="text-lg flex items-center gap-2">
              <ShieldAlert size={18} /> VirusTotal
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Detections</span>
              <Badge variant="destructive" className="bg-red-500/20 text-red-500">14 / 89</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Last Analysis</span>
              <span className="font-mono text-white">2023-10-24 14:00Z</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Associated Hashes</span>
              <span className="font-mono text-white">24</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="border-b border-gray-800">
            <CardTitle className="text-lg flex items-center gap-2">
              <ShieldCheck size={18} /> GreyNoise
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Classification</span>
              <Badge className="bg-orange-500/20 text-orange-500 border-orange-500/50">Malicious</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Actor</span>
              <span className="text-white">Unknown</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Tags</span>
              <div className="flex gap-1">
                <Badge variant="secondary" className="text-[10px]">SSH Scanner</Badge>
                <Badge variant="secondary" className="text-[10px]">Mirai</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card className="bg-gray-900 border-gray-800 flex-1">
        <CardHeader className="border-b border-gray-800">
          <CardTitle>Recent Observations in Environment</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Sensor</TableHead>
                <TableHead>Incident</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-mono text-xs text-gray-400">2023-10-24 14:32:01</TableCell>
                <TableCell className="font-mono text-xs">eu-west-1a-ssh</TableCell>
                <TableCell><Badge variant="destructive" className="bg-red-500/20 text-red-500 border-red-500/50">INC-2041</Badge></TableCell>
                <TableCell>SSH Brute Force</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

    </div>
  );
}
