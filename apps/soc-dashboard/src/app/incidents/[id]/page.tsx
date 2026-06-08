import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Clock, ShieldAlert, Activity, Globe, Server, Code, FileText, CheckCircle2 } from 'lucide-react';

export default function IncidentDetails({ params }: { params: { id: string } }) {
  const events = [
    { time: '14:28:12', type: 'Initial Access', desc: 'Multiple failed SSH attempts (Brute Force)', icon: ShieldAlert, color: 'text-orange-500', bg: 'bg-orange-500/10' },
    { time: '14:32:01', type: 'Privilege Escalation', desc: 'Successful login with root credentials', icon: Server, color: 'text-red-500', bg: 'bg-red-500/10' },
    { time: '14:35:45', type: 'Execution', desc: 'Suspicious bash script downloaded via curl', icon: Code, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
    { time: '14:36:10', type: 'Defense Evasion', desc: 'Auditd service stopped by root user', icon: Activity, color: 'text-red-500', bg: 'bg-red-500/10' },
  ];

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex flex-col gap-4">
        <Link href="/" className="text-blue-500 hover:text-blue-400 flex items-center gap-2 text-sm font-medium w-fit">
          <ArrowLeft size={16} /> Back to Incident Feed
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-3xl font-bold">SSH Brute Force Campaign</h2>
              <Badge variant="destructive">CRITICAL</Badge>
              <Badge variant="secondary">INC-2041</Badge>
            </div>
            <p className="text-gray-400 flex items-center gap-2">
              <Clock size={16} /> Started: 2023-10-24 14:28:12 UTC
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">Assign to Me</Button>
            <Button className="bg-blue-600 hover:bg-blue-500">Change Status</Button>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-1">
        
        {/* Timeline Column */}
        <div className="xl:col-span-2 space-y-6">
          <Card className="bg-gray-900 border-gray-800 h-full">
            <CardHeader className="border-b border-gray-800">
              <CardTitle>Attack Timeline</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="relative border-l-2 border-gray-800 ml-4 space-y-8">
                {events.map((event, i) => {
                  const Icon = event.icon;
                  return (
                    <div key={i} className="relative pl-8">
                      <div className={`absolute -left-[21px] top-1 p-2 rounded-full border-4 border-gray-900 ${event.bg}`}>
                        <Icon size={16} className={event.color} />
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="text-sm font-mono text-gray-500">{event.time}</span>
                        <h4 className="text-lg font-semibold text-gray-200">{event.type}</h4>
                        <p className="text-gray-400 text-sm">{event.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Threat Intel Column */}
        <div className="space-y-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800">
              <CardTitle className="flex items-center gap-2">
                <Globe size={18} className="text-blue-500"/>
                Threat Intelligence Context
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div>
                <span className="text-sm text-gray-500 block mb-1">Attacker IP</span>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-red-400 text-lg">192.168.1.105</span>
                  <Badge variant="destructive">Malicious</Badge>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-950 p-3 rounded-lg border border-gray-800">
                  <span className="text-xs text-gray-500 block">VirusTotal</span>
                  <span className="text-red-400 font-bold">54/89</span>
                </div>
                <div className="bg-gray-950 p-3 rounded-lg border border-gray-800">
                  <span className="text-xs text-gray-500 block">GreyNoise</span>
                  <span className="text-orange-400 font-bold">Scanning</span>
                </div>
              </div>
              <div className="space-y-2">
                <span className="text-sm text-gray-500 block">Identified IOCs</span>
                <div className="flex items-center gap-2 bg-gray-950 p-2 rounded border border-gray-800">
                  <FileText size={14} className="text-gray-400" />
                  <span className="font-mono text-sm text-gray-300 truncate">install_rootkit.sh</span>
                </div>
                <div className="flex items-center gap-2 bg-gray-950 p-2 rounded border border-gray-800">
                  <Code size={14} className="text-gray-400" />
                  <span className="font-mono text-sm text-gray-300 truncate">a7b8c9...d4e5f6</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800">
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 size={18} className="text-green-500"/>
                Recommended Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-3">
              <Button variant="outline" className="w-full justify-start gap-3">
                <Globe size={16} className="text-red-400"/> Block IP at Firewall
              </Button>
              <Button variant="outline" className="w-full justify-start gap-3">
                <Server size={16} className="text-yellow-400"/> Isolate Sensor
              </Button>
              <Button variant="outline" className="w-full justify-start gap-3">
                <FileText size={16} className="text-blue-400"/> Export IOCs to SIEM
              </Button>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
