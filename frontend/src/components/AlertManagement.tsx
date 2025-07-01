// medassistant/frontend/src/components/AlertManagement.tsx

import React, { useEffect, useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";

interface AlertItem {
  id: number;
  category: string;
  related_item_id: number | null;
  sensor_id: number | null;
  timestamp: string; // ISO timestamp
  message: string;
  severity: string; // "info" | "warning" | "critical"
  resolved: boolean;
  resolved_at: string | null;
}

const AlertManagement: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const resp = await axios.get<AlertItem[]>("/api/alerts/", {
        params: { status: "active" },
      });
      setAlerts(resp.data);
    } catch (err) {
      console.error("Failed to fetch alerts", err);
      toast.error("Could not load alerts");
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (id: number) => {
    try {
      await axios.post<AlertItem>(`/api/alerts/${id}/resolve`);
      toast.success("Alert resolved");
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      console.error("Failed to resolve alert", err);
      toast.error("Could not resolve alert");
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  if (loading) {
    return <div>Loading alerts…</div>;
  }

  if (alerts.length === 0) {
    return <div className="text-center py-4 text-gray-500">No active alerts.</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 bg-white shadow rounded-lg">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Message</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {alerts.map((alert) => (
            <tr key={alert.id}>
              <td className="px-4 py-2 whitespace-nowrap text-sm">
                {new Date(alert.timestamp).toLocaleString()}
              </td>
              <td className="px-4 py-2 whitespace-nowrap text-sm capitalize">
                {alert.severity}
              </td>
              <td className="px-4 py-2 text-sm">{alert.message}</td>
              <td className="px-4 py-2 whitespace-nowrap text-sm">
                <button
                  onClick={() => resolveAlert(alert.id)}
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Resolve
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AlertManagement;
