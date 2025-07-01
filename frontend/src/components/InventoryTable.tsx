// medassistant/frontend/src/components/InventoryTable.tsx

import React, { useEffect, useState } from "react";
import axios from "axios";

interface Location {
  id: number;
  name: string;
  address?: string;
}

interface Item {
  id: number;
  nfc_tag: string;
  name: string;
  batch: string;
  expiry_date: string; // ISO date
  status: string;
  location: Location;
}

const InventoryTable: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [sortField, setSortField] = useState<keyof Item>("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const fetchItems = async () => {
    setLoading(true);
    try {
      const resp = await axios.get<Item[]>("/api/items/", {
        params: {
          q,
          sort: sortField,
          order: sortOrder,
          limit: 100,
          offset: 0,
        },
      });
      setItems(resp.data);
    } catch (err) {
      console.error("Failed to fetch items", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
    // refetch when search or sorting changes
  }, [q, sortField, sortOrder]);

  const toggleSort = (field: keyof Item) => {
    if (sortField === field) {
      setSortOrder(prev => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  if (loading) {
    return <div className="p-4">Loading inventory…</div>;
  }

  return (
    <div>
      <div className="flex items-center mb-4 space-x-2">
        <input
          type="text"
          placeholder="Search items..."
          value={q}
          onChange={e => setQ(e.target.value)}
          className="flex-1 rounded border p-2"
        />
        <button
          onClick={fetchItems}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Search
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {[
                { label: "Name", field: "name" },
                { label: "Batch", field: "batch" },
                { label: "Expiry", field: "expiry_date" },
                { label: "Status", field: "status" },
                { label: "Location", field: "location" },
              ].map(col => (
                <th
                  key={col.field}
                  onClick={() => toggleSort(col.field as keyof Item)}
                  className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer"
                >
                  <div className="flex items-center">
                    {col.label}
                    {sortField === col.field && (
                      <span className="ml-1 text-gray-400">
                        {sortOrder === "asc" ? "▲" : "▼"}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.map(item => (
              <tr key={item.id}>
                <td className="px-4 py-2 whitespace-nowrap">{item.name}</td>
                <td className="px-4 py-2 whitespace-nowrap">{item.batch}</td>
                <td className="px-4 py-2 whitespace-nowrap">
                  {new Date(item.expiry_date).toLocaleDateString()}
                </td>
                <td className="px-4 py-2 whitespace-nowrap capitalize">
                  {item.status.replace("_", " ")}
                </td>
                <td className="px-4 py-2 whitespace-nowrap">
                  {item.location.name}
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-2 text-center text-gray-500">
                  No items found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InventoryTable;
