import React, { useState } from 'react';
import { LayoutDashboard, Settings, Activity, Clock } from 'lucide-react';
import { IncidentList, Incident } from './components/IncidentList';

function App() {
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  return (
    <div className="flex h-screen bg-primary text-textPrimary font-sans">
      {/* Sidebar Navigation (Left Column) */}
      <div className="w-[240px] flex-shrink-0 bg-surface border-r border-borderDefault flex flex-col">
        <div className="p-4 border-b border-borderDefault flex items-center h-16 cursor-pointer" onClick={() => setSelectedIncident(null)}>
          <h1 className="text-xl font-bold text-textPrimary tracking-tight">AutoOps</h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-2 mt-2">
          <button onClick={() => setSelectedIncident(null)} className="w-full flex items-center space-x-3 text-textPrimary bg-element px-3 py-2.5 rounded-md shadow-sm">
            <LayoutDashboard size={18} className="text-info-text" />
            <span className="font-medium text-sm">Dashboard</span>
          </button>
          <a href="#" className="flex items-center space-x-3 text-textSecondary hover:text-textPrimary hover:bg-element px-3 py-2.5 rounded-md transition-colors">
            <Activity size={18} />
            <span className="font-medium text-sm">Telemetry Config</span>
          </a>
          <a href="#" className="flex items-center space-x-3 text-textSecondary hover:text-textPrimary hover:bg-element px-3 py-2.5 rounded-md transition-colors">
            <Clock size={18} />
            <span className="font-medium text-sm">History</span>
          </a>
        </nav>
        
        <div className="p-4 border-t border-borderDefault">
          <a href="#" className="flex items-center space-x-3 text-textSecondary hover:text-textPrimary hover:bg-element px-3 py-2.5 rounded-md transition-colors">
            <Settings size={18} />
            <span className="font-medium text-sm">Settings</span>
          </a>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col min-w-0 bg-primary">
        {!selectedIncident ? (
          // Dashboard View
          <div className="flex-1 flex flex-col p-8 overflow-auto">
            <div className="max-w-5xl mx-auto w-full">
              <h2 className="text-2xl font-semibold mb-6">Active Incidents</h2>
              <div className="bg-surface rounded-lg border border-borderDefault overflow-hidden shadow-sm">
                <IncidentList onSelect={setSelectedIncident} />
              </div>
            </div>
          </div>
        ) : (
          // Incident Detail Workspace Split Layout
          <>
            <header className="h-16 flex items-center px-6 border-b border-borderDefault bg-surface shrink-0 justify-between">
              <div>
                <h2 className="text-lg font-semibold text-textPrimary flex items-center space-x-3">
                  <span className="bg-critical border border-critical-border text-critical-text px-2 py-0.5 rounded text-xs font-bold shadow-sm">Alert</span>
                  <span>{selectedIncident.alert_name}</span>
                </h2>
                <div className="flex space-x-4 text-xs text-textSecondary mt-1.5 font-medium">
                  <span>Triggered: {new Date(selectedIncident.created_at).toLocaleTimeString()}</span>
                  <span className="flex items-center space-x-1.5">
                    <span>Status:</span> 
                    <span className="text-info-text bg-info/20 px-1.5 rounded uppercase">{selectedIncident.status}</span>
                  </span>
                  <span>ID: <span className="font-mono text-[10px]">{selectedIncident.id}</span></span>
                </div>
              </div>
              <button 
                onClick={() => setSelectedIncident(null)}
                className="text-xs bg-element hover:bg-borderDefault px-3 py-1.5 rounded transition-colors text-textPrimary font-semibold"
              >
                &larr; Back to Dashboard
              </button>
            </header>

            {/* Split Pane Workspace */}
            <div className="flex-1 flex overflow-hidden">
              
              {/* Left Panel: Reasoner Node Graph (60%) */}
              <div className="flex-[6] border-r border-borderDefault bg-primary flex flex-col">
                <div className="p-4 border-b border-borderDefault bg-surface/50">
                  <h3 className="text-xs font-bold text-textSecondary uppercase tracking-wider">Reasoner Node Graph</h3>
                </div>
                
                {/* Visualizer Canvas Placeholder */}
                <div className="flex-1 overflow-auto p-8 flex flex-col items-center space-y-6">
                  
                  <div className="bg-surface border border-borderDefault rounded-md p-3 w-64 shadow-sm text-center flex flex-col items-center">
                    <span className="text-xs text-textMuted uppercase font-bold mb-1 tracking-wider">Start</span>
                    <span className="text-sm font-medium">Initialize</span>
                  </div>
                  
                  <div className="h-8 w-px bg-borderDefault"></div>
                  
                  <div className="bg-surface border border-borderFocus shadow-[0_0_10px_rgba(59,130,246,0.15)] rounded-md p-3 w-64 text-center flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-info-text rounded-full animate-pulse shadow-[0_0_5px_rgba(96,165,250,0.8)]"></span>
                      <span className="text-sm font-medium text-info-text">Query Metrics</span>
                    </div>
                    <span className="text-[10px] bg-element text-textSecondary px-1.5 py-0.5 rounded border border-borderDefault">PROMETHEUS</span>
                  </div>
                  
                  <div className="h-8 w-px bg-borderDefault"></div>
                  
                  <div className="bg-surface border border-borderDefault rounded-md p-3 w-64 text-center flex items-center justify-between opacity-50">
                    <div className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-textMuted rounded-full"></span>
                      <span className="text-sm font-medium text-textMuted">Query Logs</span>
                    </div>
                    <span className="text-[10px] bg-element text-textSecondary px-1.5 py-0.5 rounded border border-borderDefault">LOKI</span>
                  </div>
                </div>
              </div>

              {/* Right Panel: Investigation Timeline & Chat (40%) */}
              <div className="flex-[4] flex flex-col bg-surface">
                
                {/* Triage Timeline */}
                <div className="flex-1 overflow-auto border-b border-borderDefault flex flex-col">
                  <div className="p-4 border-b border-borderDefault bg-surface/50 sticky top-0 z-10">
                    <h3 className="text-xs font-bold text-textSecondary uppercase tracking-wider">Triage Timeline Feed</h3>
                  </div>
                  
                  <div className="p-4 space-y-6">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-mono text-textMuted">Pending...</span>
                        <span className="text-xs font-bold text-info-text">[Agent]</span>
                      </div>
                      <div className="text-sm text-textPrimary bg-primary border border-borderDefault p-3 rounded-md shadow-sm italic text-textMuted">
                        LangGraph integration is scheduled for Milestone 2.
                      </div>
                    </div>
                  </div>
                </div>

                {/* Chat Input */}
                <div className="p-4 bg-primary shrink-0">
                  <div className="text-xs font-bold text-textSecondary uppercase tracking-wider mb-3">Ad-Hoc Agent Chat</div>
                  <div className="relative">
                    <input 
                      type="text" 
                      placeholder="Ask a follow-up question..." 
                      className="w-full bg-element border border-borderDefault text-textPrimary text-sm px-4 py-3 rounded-md shadow-inner focus:outline-none focus:border-borderFocus focus:ring-1 focus:ring-borderFocus transition-all placeholder:text-textMuted"
                    />
                    <button className="absolute right-2 top-2 bottom-2 bg-info hover:bg-info/80 text-info-text border border-info-border px-3 rounded text-xs font-semibold transition-colors">
                      Send
                    </button>
                  </div>
                </div>
                
              </div>
            </div>

            {/* Bottom Panel: Remediation */}
            <div className="shrink-0 p-4 bg-surface border-t border-borderDefault">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-semibold text-textSecondary">Suggested Remediation:</span>
                  <span className="text-sm text-textMuted italic">Awaiting agent analysis...</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
