import { Activity, ShieldAlert, AlertTriangle, KeyRound, Server } from 'lucide-react';

export function AlertCorrelationGraph() {
  const steps = [
    { icon: Globe, label: 'Attacker IP', detail: '192.168.1.105', color: 'text-red-500', bg: 'bg-red-500/10' },
    { icon: Activity, label: 'Reconnaissance', detail: 'HTTP Port Scan', color: 'text-orange-500', bg: 'bg-orange-500/10' },
    { icon: KeyRound, label: 'Credential Access', detail: 'SSH Brute Force', color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
    { icon: Server, label: 'Command Execution', detail: 'wget rootkit.sh', color: 'text-red-500', bg: 'bg-red-500/10' },
    { icon: ShieldAlert, label: 'Incident Triggered', detail: 'INC-2041', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  ];

  return (
    <div className="flex flex-col md:flex-row items-center justify-between w-full px-4 py-8 overflow-x-auto">
      {steps.map((step, index) => {
        const Icon = step.icon;
        return (
          <div key={index} className="flex items-center">
            <div className="flex flex-col items-center gap-3 w-32 text-center">
              <div className={`p-4 rounded-full border-2 border-gray-800 ${step.bg}`}>
                <Icon size={24} className={step.color} />
              </div>
              <div>
                <p className="font-semibold text-sm text-gray-200">{step.label}</p>
                <p className="text-xs text-gray-500 font-mono mt-1">{step.detail}</p>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div className="h-px w-8 md:w-16 bg-gray-700 mx-2 flex-shrink-0 relative">
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-t-2 border-r-2 border-gray-700 rotate-45 transform origin-center"></div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// Temporary mock Globe import since it's not exported from lucide-react directly in this scope easily without explicit import
import { Globe } from 'lucide-react';
