import React, { useEffect, useState } from 'react';

export interface Incident {
  id: string;
  status: string;
  alert_name: string;
  created_at: string;
  resolved_at: string | null;
  root_cause_summary: string | null;
  remediation_steps: string[];
  confidence_score: number;
}

export function IncidentList({ onSelect }: { onSelect: (incident: Incident) => void }) {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/incidents')
      .then(res => res.json())
      .then(data => {
        setIncidents(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch incidents", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-textMuted font-medium">Loading incidents...</div>;
  }

  if (incidents.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="text-textMuted font-medium mb-2">No incidents found.</div>
        <div className="text-xs text-textSecondary">Wait for Alertmanager webhooks or manually trigger one.</div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="bg-element text-textSecondary uppercase text-xs">
          <tr>
            <th className="px-6 py-3 border-b border-borderDefault font-semibold">Status</th>
            <th className="px-6 py-3 border-b border-borderDefault font-semibold">Alert Name</th>
            <th className="px-6 py-3 border-b border-borderDefault font-semibold">Triggered At</th>
            <th className="px-6 py-3 border-b border-borderDefault font-semibold text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-borderDefault">
          {incidents.map((incident) => (
            <tr key={incident.id} className="hover:bg-element/50 transition-colors">
              <td className="px-6 py-4">
                <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase shadow-sm ${
                  incident.status === 'investigating' ? 'bg-info/20 text-info-text border border-info-border' :
                  incident.status === 'resolved' ? 'bg-success/20 text-success-text border border-success-border' :
                  'bg-warning/20 text-warning-text border border-warning-border'
                }`}>
                  {incident.status}
                </span>
              </td>
              <td className="px-6 py-4 font-medium text-textPrimary">{incident.alert_name}</td>
              <td className="px-6 py-4 text-textMuted font-mono text-xs">{new Date(incident.created_at).toLocaleString()}</td>
              <td className="px-6 py-4 text-right">
                <button 
                  onClick={() => onSelect(incident)}
                  className="bg-element hover:bg-borderDefault text-textPrimary text-xs font-semibold px-3 py-1.5 rounded transition-colors"
                >
                  Investigate
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
