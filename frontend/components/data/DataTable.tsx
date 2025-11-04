'use client';

interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
}

export default function DataTable<T extends Record<string, any>>({
  columns,
  data,
  onRowClick,
}: DataTableProps<T>) {
  return (
    <div className="bg-white rounded-lg border border-neutral-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-neutral-50 border-b border-neutral-200">
            <tr>
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className="px-4 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200">
            {data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                onClick={() => onRowClick?.(row)}
                className={onRowClick ? 'cursor-pointer hover:bg-neutral-50 transition-colors' : ''}
              >
                {columns.map((column) => (
                  <td key={String(column.key)} className="px-4 py-3 text-sm text-neutral-900">
                    {column.render
                      ? column.render(row)
                      : typeof column.key === 'string'
                      ? row[column.key]
                      : row[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.length === 0 && (
        <div className="p-12 text-center text-neutral-500">No data available</div>
      )}
    </div>
  );
}

