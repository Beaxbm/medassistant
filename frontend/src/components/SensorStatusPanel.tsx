// medassistant/frontend/src/components/SensorStatusPanel.tsx

import React, { useEffect, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import {
  Thermometer,
  Droplet,
  Zap,
  DoorOpen,
  WifiOff,
} from "lucide-react";

interface SensorStatusItem {
  sensor_id: number;
  name: string;
  type: string;
  last_ping: string | null;
  value: number | null;
  threshold_min: number | null;
  threshold_max: number | null;
  status: "ok" | "warning" | "danger" | "offline";
}

const ICONS: Record<string, React.FC<any>> = {
  temperature: Thermometer,
  humidity: Droplet,
  power: Zap,
  door: DoorOpen,
};

const STATUS_STYLES: Record<SensorStatusItem["status"], string> = {
  ok: "bg-green-100 text-green-800",
  warning: "bg-yellow-100 text-yellow-800",
  danger: "bg-red-100 text-red-800",
  offline: "bg-gray-100 text-gray-500",
};

const POLL_INTERVAL = 30_000; // 30 seconds

const SensorStatusPanel: React.FC = () => {
  const [sensors, setSensors] = useState<SensorStatusItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const resp = await axios.get<SensorStatusItem[]>(
        "/api/sensors/status/"
      );
      setSensors(resp.data);
    } catch (err) {
      console.error("Failed to fetch sensor status", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div>Loading sensors…</div>;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {sensors.map((s) => {
        const Icon = ICONS[s.type] || WifiOff;
        return (
          <motion.div
            key={s.sensor_id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex items-center space-x-3 rounded-lg p-4 shadow-sm ${
              STATUS_STYLES[s.status]
            }`}
          >
            <div className="p-2 rounded-full bg-white">
              <Icon className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-medium">{s.name}</h3>
              <p className="text-sm">
                {s.value !== null
                  ? `${s.value} ${
                      s.type === "temperature" ? "°C" : s.type === "humidity" ? "%" : ""
                    }`
                  : "No data"}
              </p>
              <p className="text-xs opacity-75">
                Last ping:{" "}
                {s.last_ping
                  ? new Date(s.last_ping).toLocaleTimeString()
                  : "—"}
              </p>
            </div>
            <span
              className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold`}
            >
              {s.status.toUpperCase()}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
};

export default SensorStatusPanel;
